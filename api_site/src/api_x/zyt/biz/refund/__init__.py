# coding=utf-8
from __future__ import unicode_literals
from decimal import InvalidOperation, Decimal

from api_x import db
from api_x.zyt.biz.commons import is_duplicated_notify
from api_x.zyt.biz.transaction.dba import get_tx_by_id
from api_x.zyt.vas.bookkeep import bookkeeping
from api_x.zyt.user_mapping import get_system_account_user_id
from api_x.constant import SECURE_USER_NAME, PaymentTxState, RefundTxState, TxState
from api_x.zyt.vas.user import get_user_cash_balance
from api_x.zyt.biz import user_roles
from pytoolbox.util.dbs import transactional, require_transaction_context
from api_x.zyt.biz.models import UserRole
from ...vas.models import EventType
from ..transaction import create_transaction, transit_transaction_state, update_transaction_info
from ..transaction import add_tx_user
from ..models import TransactionType, RefundRecord, PaymentType
from .error import *
from api_x.utils.entry_auth import verify_call_perm
from api_x.zyt.biz.error import *
from api_x.zyt.biz.transaction.dba import get_tx_by_sn
from pytoolbox.util.log import get_logger
from api_x.task import tasks


logger = get_logger(__name__)


def apply_to_refund(channel, order_id, amount, client_notify_url, data=None):
    payment_tx = _get_payment_tx_to_refund(channel.id, order_id)

    try:
        amount_value = Decimal(amount)
    except InvalidOperation:
        raise AmountValueError(amount)
    if amount_value <= 0:
        raise NonPositiveAmountError(amount_value)

    refund_record = create_and_request_refund(channel, payment_tx, amount_value, client_notify_url, data=data)

    return refund_record


def handle_refund_in(vas_name, sn, notify_handle=None):
    tx = get_tx_by_sn(sn)
    refund_record = tx.record
    payment_tx = tx.super
    _succeed_refund_in(vas_name, payment_tx, refund_record)

    if notify_handle is not None:
        notify_handle(True)


def handle_refund_notify(is_success, sn, vas_name, vas_sn, data):
    """
    :param is_success: 是否成功
    :param sn: 订单号
    :param vas_name: 来源系统
    :param vas_sn: 来源系统订单号
    :param data: 数据
    :return:
    """
    import time
    tx = get_tx_by_sn(sn)
    if tx is None:
        for i in range(10):
            # 这是因为_create_and_request_refund在一个事务中，notify到这儿的时候，事务没有结束，导致tx获取不到。
            # 这里的解决办法就是重试
            tx = get_tx_by_sn(sn)
            if tx is None:
                logger.warn('apply refund [{0}] is not finish, sleep then retry.')
                time.sleep(0.5)
                continue
            break
    refund_record = tx.record

    logger.info('refund notify: {0}, {1}, {2}, {3}, {4}'.format(is_success, sn, vas_name, vas_sn, data))
    if tx is None or refund_record is None:
        # 不存在
        logger.warning('refund [{0}] not exits.'.format(sn))
        return

    if is_duplicated_notify(tx, vas_name, vas_sn):
        logger.warning('refund notify duplicated: [{0}, {1}]'.format(vas_name, vas_sn))
        return

    if tx.state not in [RefundTxState.PROCESSING, RefundTxState.REFUNDED_IN]:
        logger.warning('bad refund notify: [sn: {0}]'.format(sn))
        return

    payment_tx = tx.super
    payment_record = payment_tx.record

    if payment_tx.state != PaymentTxState.REFUNDING:
        logger.warning('bad refund notify: [sn: {0}], [payment_sn: {1}]'.format(sn, payment_tx.sn))
        return

    with require_transaction_context():
        tx = update_transaction_info(refund_record.tx_id, vas_sn)
        if is_success:
            handle_succeed_refund(vas_name, payment_record, refund_record)
        else:
            handle_fail_refund(payment_record, refund_record)

    # notify client.
    tx = get_tx_by_id(tx.id)
    _try_notify_client(tx, refund_record)


def _try_notify_client(tx, refund_record):
    from api_x.utils.notify import sign_and_notify_client
    url = refund_record.client_notify_url
    if not url:
        return

    params = None
    if tx.state == RefundTxState.SUCCESS:
        params = {'code': 0, 'order_id': refund_record.order_id, 'amount': refund_record.amount}
    elif tx.state == RefundTxState.FAILED:
        params = {'code': 1, 'order_id': refund_record.order_id, 'amount': refund_record.amount}

    # notify
    sign_and_notify_client(url, params, tx.channel_name, task=tasks.refund_notify)


def _get_payment_tx_to_refund(channel_id, order_id):
    from api_x.zyt.biz.pay.dba import get_payment_by_channel_order_id

    payment_record = get_payment_by_channel_order_id(channel_id, order_id)
    if not payment_record:
        raise NoPaymentFoundError(channel_id, order_id)

    tx = payment_record.tx

    if tx.state == TxState.FINISHED:
        # TODO: 在适当的时候设置交易结束, 比如交易创建3个月后.
        # 交易结束，不能退款
        raise TransactionFinishedError()

    if not _is_refundable(tx, payment_record):
        raise PaymentNotRefundableError()
    return tx


@verify_call_perm('refund_direct')
def _direct_payment_is_refundable(channel_name, tx):
    return tx.state == PaymentTxState.SUCCESS


def _is_refundable(tx, payment_record):
    if tx.state == PaymentTxState.REFUNDING:
        raise PaymentIsRefundingError()

    if tx.state == PaymentTxState.REFUNDED:
        raise PaymentRefundedError()

    if tx.state == PaymentTxState.CREATED:
        raise PaymentNotPaidError()

    pay_type = payment_record.type
    if pay_type == PaymentType.DIRECT:
        return _direct_payment_is_refundable(tx.channel_name, tx)
    if pay_type == PaymentType.GUARANTEE:
        return tx.state == PaymentTxState.SECURED


@transactional
def create_and_request_refund(channel, payment_tx, amount, client_notify_url, data=None):
    payment_record, refund_tx, refund_record = _create_refund(channel, payment_tx, amount, client_notify_url)

    try:
        # FIXME: 暂时忽略返回结果，无异常表明执行正常
        _request_refund(payment_tx, payment_record, refund_tx, refund_record, data=data)
    except Exception as e:
        logger.exception(e)

        # 退款余额不足
        logger.info("block refund: [{0}]".format(refund_tx.sn))
        _block_refund(refund_record)

    return refund_record


@transactional
def try_unblock_refund(refund_tx):
    refund_record = refund_tx.record
    _unblock_refund(refund_record)

    payment_sn = refund_record.payment_sn
    payment_tx = get_tx_by_sn(payment_sn)
    payment_record = payment_tx.record

    try:
        _request_refund(payment_tx, payment_record, refund_tx, refund_record)
        return True
    except Exception as e:
        logger.info("failed to unblock refund: [{0}], [{1}]".format(refund_tx.sn, e.message))
        _block_refund(refund_record)
    return False


@transactional
def _create_refund(channel, payment_tx, amount, client_notify_url):
    cur_payment_state = payment_tx.state

    # start refunding.
    transit_transaction_state(payment_tx.id, payment_tx.state, PaymentTxState.REFUNDING)

    payment_tx = get_tx_by_id(payment_tx.id)
    payment_record = payment_tx.record
    if payment_tx.state != PaymentTxState.REFUNDING:
        raise PaymentNotRefundableError()

    if amount + payment_record.refunded_amount > payment_record.paid_amount:
        raise RefundAmountError(payment_record.paid_amount, payment_record.refunded_amount, amount)

    comments = "退款-{0}".format(payment_record.product_name)

    user_ids = [user_roles.tx_to_user(payment_record.payer_id), user_roles.from_user(payment_record.payee_id)]
    if payment_record.type == PaymentType.GUARANTEE:
        secure_user_id = get_system_account_user_id(SECURE_USER_NAME)
        user_ids.append(user_roles.guaranteed_by(secure_user_id))
    elif payment_record.type == PaymentType.DIRECT:
        # check balance.
        # 直付退款时收款方余额必须足够
        balance = get_user_cash_balance(payment_record.payee_id)
        if amount > balance.available:
            raise RefundBalanceError(amount, balance.available)
    tx = create_transaction(channel.name, TransactionType.REFUND, amount, comments, user_ids,
                            super_id=payment_tx.id,
                            vas_name=payment_tx.vas_name, order_id=payment_record.order_id)

    fields = {
        'tx_id': tx.id,
        'sn': tx.sn,
        'payment_sn': payment_record.sn,
        'payment_state': cur_payment_state,
        'payer_id': payment_record.payer_id,
        'payee_id': payment_record.payee_id,
        'order_id': payment_record.order_id,
        'amount': amount,
        'client_notify_url': client_notify_url
    }

    refund_record = RefundRecord(**fields)
    db.session.add(refund_record)

    return payment_record, tx, refund_record


@transactional
def _refund_to_processing(tx):
    if tx.state == RefundTxState.CREATED:
        transit_transaction_state(tx.id, RefundTxState.CREATED, RefundTxState.PROCESSING)


def _request_refund(payment_tx, payment_record, refund_tx, refund_record, data=None):
    from api_x.zyt.evas import test_pay, lianlian_pay, weixin_pay, ali_pay
    from api_x.zyt import vas

    vas_name = payment_tx.vas_name

    if vas_name == test_pay.NAME:
        res = _refund_by_test_pay(payment_tx, refund_record, data)
    elif vas_name == lianlian_pay.NAME:
        res = _refund_by_lianlian_pay(payment_tx, refund_record)
    elif weixin_pay.is_weixin_pay(vas_name):
        res = _refund_by_weixin_pay(payment_tx, payment_record, refund_tx, refund_record)
    elif vas_name == ali_pay.NAME:
        res = _refund_by_ali_pay(payment_tx, payment_record, refund_tx, refund_record)
    elif vas_name == vas.NAME:
        res = _refund_by_zyt(refund_record)
        refund_tx = get_tx_by_sn(refund_tx.sn)
    else:
        raise RefundFailedError('unknown vas {0}'.format(vas_name))

    _refund_to_processing(refund_tx)
    return res


def _refund_by_test_pay(tx, refund_record, data=None):
    """测试支付退款"""
    from api_x.zyt.evas.test_pay import refund
    from api_x.zyt.evas.test_pay.commons import is_success_request

    vas_sn = tx.vas_sn

    sn = refund_record.sn
    amount = refund_record.amount

    result = data.get('result') if data else None
    res = refund(TransactionType.REFUND, sn, amount, vas_sn, result or 'SUCCESS')

    if not is_success_request(res):
        logger.error('request refund failed: {0}'.format(res))
        raise RefundFailedError(res['ret_msg'])

    return res


def _refund_by_lianlian_pay(tx, refund_record):
    """连连退款"""
    from api_x.zyt.evas.lianlian_pay import refund

    vas_sn = tx.vas_sn

    sn = refund_record.sn
    created_on = refund_record.created_on
    amount = refund_record.amount

    try:
        res = refund(TransactionType.REFUND, sn, created_on, amount, vas_sn)
    # except RefundBalanceInsufficientError as e:
    #     raise e
    except Exception as e:
        logger.exception(e)
        raise RefundFailedError(e.message)

    return res


def _refund_by_ali_pay(payment_tx, payment_record, refund_tx, refund_record):
    """支付宝退款"""
    from api_x.zyt.evas.ali_pay import refund

    trade_no = payment_tx.vas_sn
    out_refund_no = refund_tx.sn
    refund_fee = refund_record.amount

    try:
        res = refund(TransactionType.REFUND, out_refund_no, trade_no, refund_fee)
    except Exception as e:
        logger.exception(e)
        raise RefundFailedError()

    return res


def _refund_by_weixin_pay(payment_tx, payment_record, refund_tx, refund_record):
    """微信退款"""
    from api_x.zyt.evas.weixin_pay import get_app_config_by_vas_id
    from api_x.zyt.evas.weixin_pay.refund import refund

    transaction_id = payment_tx.vas_sn
    out_trade_no = payment_tx.sn
    out_refund_no = refund_record.sn
    total_fee = int(100 * payment_record.amount)
    refund_fee = int(100 * refund_record.amount)
    app_config = get_app_config_by_vas_id(refund_tx.vas_name)

    try:
        res = refund(out_refund_no, transaction_id, total_fee, refund_fee,
                     out_trade_no=out_trade_no, app_config=app_config)
    except Exception as e:
        logger.exception(e)
        raise RefundFailedError()

    # try to query refund notify.
    # TODO: start query refund notify task.
    return res


def _refund_by_zyt(refund_record):
    """自游通支付退款"""
    from api_x.zyt import vas

    if not vas.refund(TransactionType.REFUND, refund_record.sn):
        raise RefundFailedError()


@transactional
def handle_succeed_refund(vas_name, payment_record, refund_record):
    refund_amount = refund_record.amount

    # 直付和担保付的不同操作
    if payment_record.type == PaymentType.DIRECT:
        event_id = bookkeeping(EventType.TRANSFER_OUT, refund_record.sn, refund_record.payee_id, vas_name, refund_amount)
    elif payment_record.type == PaymentType.GUARANTEE:
        secure_user_id = get_system_account_user_id(SECURE_USER_NAME)
        event_id = bookkeeping(EventType.TRANSFER_OUT_FROZEN, refund_record.sn, secure_user_id, vas_name, refund_amount)
    else:
        logger.warn('bad payment type: [{0}]'.format(payment_record.type))
        return

    refund_tx = refund_record.tx
    transit_transaction_state(refund_tx.id, refund_tx.state,
                              RefundTxState.SUCCESS, event_id)

    payment_record.add_refund(refund_record, event_id)


@transactional
def handle_fail_refund(payment_record, refund_record):
    transit_transaction_state(payment_record.tx_id, PaymentTxState.REFUNDING, refund_record.payment_state)
    transit_transaction_state(refund_record.tx_id, RefundTxState.PROCESSING, RefundTxState.FAILED)


@transactional
def _block_refund(refund_record):
    transit_transaction_state(refund_record.tx_id, RefundTxState.CREATED, RefundTxState.BLOCK)


@transactional
def _unblock_refund(refund_record):
    transit_transaction_state(refund_record.tx_id, RefundTxState.BLOCK, RefundTxState.CREATED)


@transactional
def _succeed_refund_in(vas_name, payment_tx, refund_record):
    """处理被退款人的事务"""
    refund_amount = refund_record.amount
    from_user_role = payment_tx.get_role(UserRole.FROM)
    if from_user_role is None:
        raise BizError('payment tx error: should has from role user.')
    event_id = bookkeeping(EventType.TRANSFER_IN, refund_record.sn, from_user_role.user_id, vas_name, refund_amount)
    transit_transaction_state(refund_record.tx_id, RefundTxState.CREATED, RefundTxState.REFUNDED_IN, event_id)

    add_tx_user(refund_record.tx_id, user_roles.to_user(from_user_role.user_id))
