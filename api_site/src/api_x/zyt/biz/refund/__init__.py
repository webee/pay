# coding=utf-8
from __future__ import unicode_literals
from decimal import InvalidOperation, Decimal

from api_x import db
from api_x.zyt.biz.commons import is_duplicated_notify
from api_x.zyt.biz.refund.dba import update_payment_refunded_amount
from api_x.zyt.biz.transaction.dba import get_tx_by_id, get_tx_by_sn
from api_x.zyt.vas.bookkeep import bookkeeping
from api_x.zyt.user_mapping import get_system_account_user_id
from api_x.constant import SECURE_USER_NAME, PaymentTxState, RefundTxState
from api_x.zyt.vas.user import get_user_cash_balance
from api_x.zyt.biz.models import UserRole
from pytoolbox.util.dbs import transactional, require_transaction_context
from ...vas.models import EventType
from ..transaction import create_transaction, transit_transaction_state, update_transaction_info
from ..models import TransactionType, RefundRecord, PaymentType
from .error import *
from api_x.zyt.biz.payment.dba import get_payment_by_id, get_tx_payment_by_sn
from api_x.zyt.biz.error import *
from .dba import get_tx_refund_by_sn
from pytoolbox.util.log import get_logger
from api_x.task import tasks
from api_x.zyt.vas import NAME as ZYT_NAME


logger = get_logger(__name__)


def apply_to_refund(channel, order_id, amount, client_notify_url, data):
    payment_tx, payment_record = _get_tx_payment_to_refund(channel.id, order_id)

    # FIXME:
    # 以下事实上是拒绝所有成功的交易进行退款
    # 因为金额可能被提现出去。
    if payment_tx.state == PaymentTxState.SUCCESS:
        # disable success finished pay refund.
        raise RefundSuccessPayError(payment_tx.sn)

    try:
        amount_value = Decimal(amount)
    except InvalidOperation:
        raise AmountValueError(amount)
    if amount_value <= 0:
        raise NonPositiveAmountError(amount_value)

    refund_record = _create_and_request_refund(channel, payment_tx, payment_record, amount_value, client_notify_url, data)

    return refund_record


def handle_refund_in(sn):
    tx, refund_record = get_tx_refund_by_sn(sn)
    succeed_refund_in(ZYT_NAME, refund_record)


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
    for i in range(10):
        # 这是因为apply_refund在一个事务中，notify到这儿的时候，事务没有结束，导致tx获取不到。
        # 这里的解决办法就是重试
        tx, refund_record = get_tx_refund_by_sn(sn)
        if tx is None:
            logger.warn('apply refund [{0}] is not finish, sleep then retry.')
            time.sleep(0.5)
            continue
        break

    payment_tx, payment_record = get_tx_payment_by_sn(refund_record.payment_sn)

    logger.info('refund notify: {0}, {1}, {2}, {3}, {4}'.format(is_success, sn, vas_name, vas_sn, data))
    if tx is None or refund_record is None:
        # 不存在
        logger.warning('refund [{0}] not exits.'.format(sn))
        return

    if is_duplicated_notify(tx, vas_name, vas_sn):
        logger.warning('refund notify duplicated: [{0}, {1}]'.format(vas_name, vas_sn))
        return

    if payment_tx.state != PaymentTxState.REFUNDING and tx.state != RefundTxState.CREATED:
        logger.warning('bad refund notify: [sn: {0}]'.format(sn))
        return

    with require_transaction_context():
        tx = update_transaction_info(refund_record.tx_id, vas_sn)
        if is_success:
            # 直付和担保付的不同操作
            if payment_record.type == PaymentType.DIRECT:
                # !!impossible.
                # direct pay is not allowed to refund.
                succeed_refund(vas_name, payment_record, refund_record)
            elif payment_record.type == PaymentType.GUARANTEE:
                succeed_refund_secured(vas_name, payment_record, refund_record)
        else:
            fail_refund(payment_record, refund_record)

    # notify client.
    tx = get_tx_by_id(tx.id)
    _try_notify_client(tx, refund_record)


def _try_notify_client(tx, refund_record):
    from api_x.utils.notify import sign_and_notify_client
    url = refund_record.client_notify_url

    params = None
    if tx.state == RefundTxState.SUCCESS:
        params = {'code': 0, 'order_id': refund_record.order_id, 'amount': refund_record.amount}
    elif tx.state == RefundTxState.FAILED:
        params = {'code': 1, 'order_id': refund_record.order_id, 'amount': refund_record.amount}

    # notify
    sign_and_notify_client(url, params, tx.channel_name, task=tasks.refund_notify)


def _get_tx_payment_to_refund(channel_id, order_id):
    from api_x.zyt.biz.payment.dba import get_payment_by_channel_order_id

    payment_record = get_payment_by_channel_order_id(channel_id, order_id)
    if not payment_record:
        raise NoPaymentFoundError(channel_id, order_id)

    tx = get_tx_by_sn(payment_record.sn)
    if tx.state == PaymentTxState.REFUNDING:
        raise PaymentIsRefundingError()
    if not _is_refundable(tx, payment_record):
        raise PaymentNotRefundableError()
    return tx, payment_record


def _is_refundable(tx, payment_record):
    pay_type = payment_record.type
    if pay_type == PaymentType.DIRECT:
        raise RefundDirectPayError(tx.sn)
        # return False
        # return tx.state == PaymentTransactionState.SUCCESS
    if pay_type == PaymentType.GUARANTEE:
        return tx.state == PaymentTxState.SECURED


@transactional
def _create_and_request_refund(channel, payment_tx, payment_record, amount, client_notify_url, data):
    payment_record, refund_record = _create_refund(channel, payment_tx, payment_record, amount, client_notify_url)

    try:
        _request_refund(payment_tx, payment_record, refund_record, data)
    except Exception as e:
        logger.exception(e)
        # FIXME: because this is in a transaction, below is useless.
        fail_refund(payment_record, refund_record)
        raise RefundFailedError(e.message)

    return refund_record


@transactional
def _create_refund(channel, payment_tx, payment_record, amount, client_notify_url):
    cur_payment_state = payment_tx.state

    # start refunding.
    transit_transaction_state(payment_tx.id, payment_tx.state, PaymentTxState.REFUNDING)

    payment_tx = get_tx_by_id(payment_tx.id)
    payment_record = get_payment_by_id(payment_record.id)
    if payment_tx.state != PaymentTxState.REFUNDING:
        raise PaymentNotRefundableError()

    if amount + payment_record.refunded_amount > payment_record.amount:
        raise RefundAmountError(payment_record.amount, payment_record.refunded_amount, amount)

    comments = "退款-{0}".format(payment_record.product_name)

    user_ids = [(payment_record.payer_id, UserRole.TO), (payment_record.payee_id, UserRole.FROM)]
    if payment_record.type == PaymentType.GUARANTEE:
        secure_user_id = get_system_account_user_id(SECURE_USER_NAME)
        user_ids.append((secure_user_id, UserRole.GUARANTOR))
    elif payment_record.type == PaymentType.DIRECT:
        # check balance.
        # 直付退款时收款方余额必须足够
        balance = get_user_cash_balance(payment_record.payee_id)
        if amount > balance.available:
            raise RefundBalanceError(amount, balance.available)
    tx_record = create_transaction(channel.name, TransactionType.REFUND, amount, comments, user_ids,
                                   vas_name=payment_tx.vas_name, order_id=payment_record.order_id)

    fields = {
        'tx_id': tx_record.id,
        'sn': tx_record.sn,
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

    return payment_record, refund_record


def _request_refund(payment_tx, payment_record, refund_record, data):
    from api_x.zyt.evas import test_pay, lianlian_pay
    from api_x.zyt import vas

    vas_name = payment_tx.vas_name

    if vas_name == test_pay.NAME:
        return _refund_by_test_pay(payment_tx, refund_record, data)
    if vas_name == lianlian_pay.NAME:
        return _refund_by_lianlian_pay(payment_tx, refund_record)
    if vas_name == vas.NAME:
        return vas.refund(TransactionType.REFUND, refund_record.sn)
    raise RefundFailedError('unknown vas {0}'.format(vas_name))


def _refund_by_test_pay(tx, refund_record, data):
    """测试支付退款"""
    from api_x.zyt.evas.test_pay import refund
    from api_x.zyt.evas.test_pay.commons import is_success_request

    vas_sn = tx.vas_sn

    sn = refund_record.sn
    amount = refund_record.amount

    result = data.get('result')
    res = refund(TransactionType.REFUND, sn, amount, vas_sn, result or 'SUCCESS')

    if not is_success_request(res):
        logger.error('request refund failed: {0}'.format(res))
        raise RefundFailedError(res['ret_msg'])

    return res


def _refund_by_lianlian_pay(tx, refund_record):
    """连连退款"""
    from api_x.zyt.evas.lianlian_pay import refund
    from api_x.zyt.evas.lianlian_pay.commons import is_success_request

    vas_sn = tx.vas_sn

    sn = refund_record.sn
    created_on = refund_record.created_on
    amount = refund_record.amount

    res = refund(TransactionType.REFUND, sn, created_on, amount, vas_sn)

    if not is_success_request(res):
        logger.error('request refund failed: {0}'.format(res))
        raise RefundFailedError(res['ret_msg'])

    # try to query refund notify.
    # TODO: start query refund notify task.
    return res


@transactional
def succeed_refund(vas_name, payment_record, refund_record):
    payment_amount = payment_record.amount
    refunded_amount = payment_record.refunded_amount
    refund_amount = refund_record.amount
    event_id = bookkeeping(EventType.TRANSFER_OUT, refund_record.sn, refund_record.payee_id, vas_name, refund_amount)

    # 全部金额都退款，则状态为已退款
    is_refunded = payment_amount == refunded_amount + refund_amount

    if is_refunded:
        transit_transaction_state(payment_record.tx_id, PaymentTxState.REFUNDING,
                                  PaymentTxState.REFUNDED, event_id)
    else:
        transit_transaction_state(payment_record.tx_id, PaymentTxState.REFUNDING,
                                  refund_record.payment_state, event_id)

    transit_transaction_state(refund_record.tx_id, RefundTxState.CREATED,
                              RefundTxState.SUCCESS, event_id)

    update_payment_refunded_amount(payment_record.id, refund_amount)


@transactional
def succeed_refund_secured(vas_name, payment_record, refund_record):
    payment_amount = payment_record.amount
    refunded_amount = payment_record.refunded_amount
    refund_amount = refund_record.amount
    secure_user_id = get_system_account_user_id(SECURE_USER_NAME)
    event_id = bookkeeping(EventType.TRANSFER_OUT_FROZEN, payment_record.sn, secure_user_id, vas_name, refund_amount)

    # 全部金额都退款，则状态为已退款
    is_refunded = payment_amount == refunded_amount + refund_amount

    if is_refunded:
        transit_transaction_state(payment_record.tx_id, PaymentTxState.REFUNDING,
                                  PaymentTxState.REFUNDED, event_id)
    else:
        transit_transaction_state(payment_record.tx_id, PaymentTxState.REFUNDING,
                                  refund_record.payment_state, event_id)
    transit_transaction_state(refund_record.tx_id, RefundTxState.CREATED,
                              RefundTxState.SUCCESS, event_id)

    update_payment_refunded_amount(payment_record.id, refund_amount)


@transactional
def fail_refund(payment_record, refund_record):
    transit_transaction_state(payment_record.tx_id, PaymentTxState.REFUNDING, refund_record.payment_state)
    transit_transaction_state(refund_record.tx_id, RefundTxState.CREATED, RefundTxState.FAILED)


@transactional
def succeed_refund_in(vas_name, refund_record):
    refund_amount = refund_record.amount
    event_id = bookkeeping(EventType.TRANSFER_IN, refund_record.sn, refund_record.payer_id, vas_name, refund_amount)

    # 此处应该已经退款
    transit_transaction_state(refund_record.tx_id, RefundTxState.SUCCESS, RefundTxState.SUCCESS, event_id)
