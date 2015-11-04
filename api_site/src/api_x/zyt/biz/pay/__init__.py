# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.biz.commons import is_duplicated_notify
from api_x.zyt.biz.pay.dba import get_payment_by_channel_order_id, get_payment_by_sn, get_payment_tx_by_sn
from api_x.zyt.biz.transaction.dba import get_tx_by_id

import time
from decimal import InvalidOperation, Decimal
from api_x import db
from api_x.zyt.vas.bookkeep import bookkeeping
from api_x.zyt.vas.pattern import zyt_bookkeeping
from api_x.zyt.user_mapping import get_system_account_user_id, get_user_map_by_account_user_id
from api_x.constant import SECURE_USER_NAME, PaymentTxState
from api_x.zyt.vas.models import EventType
from api_x.zyt.biz.transaction import create_transaction, transit_transaction_state, update_transaction_info
from api_x.zyt.biz.models import TransactionType, PaymentRecord, PaymentType, TransactionSnStack
from api_x.zyt.biz.error import NonPositiveAmountError, NegativeAmountError
from api_x.zyt.biz.error import TransactionNotFoundError, AmountValueError
from api_x.zyt.biz.transaction.error import TransactionStateError
from api_x.zyt.biz.models import DuplicatedPaymentRecord
from api_x.zyt.biz import user_roles
from pytoolbox.util.dbs import require_transaction_context, transactional
from pytoolbox.util.log import get_logger
from api_x.config import etc as config
from api_x.task import tasks
from .error import AlreadyPaidError


logger = get_logger(__name__)


def find_or_create_payment(channel, payment_type, payer_id, payee_id, order_id,
                           product_name, product_category, product_desc, amount,
                           client_callback_url, client_notify_url):
    """
    如果金额为0, 则本次新建订单操作失败
    如果已经有对应订单，则直接支付成功
    """
    payment_record = PaymentRecord.query.filter_by(channel_id=channel.id, order_id=order_id).first()

    try:
        amount = Decimal(amount)
    except InvalidOperation:
        raise AmountValueError(amount)

    if payment_record is None:
        if amount <= 0:
            raise NonPositiveAmountError(amount)

        payment_record = _create_payment(channel, payment_type, payer_id, payee_id, order_id,
                                         product_name, product_category, product_desc, amount,
                                         client_callback_url, client_notify_url)
    else:
        payment_record = _restart_payment(channel, payment_record, amount, product_name, product_category, product_desc)

    if payment_record.amount < 0:
        raise NegativeAmountError(payment_record.amount)

    if payment_record.amount == 0:
        # 直接成功
        from api_x.zyt import vas as zyt

        tx = update_transaction_info(payment_record.tx_id, payment_record.sn,
                                     vas_name=zyt.NAME, state=PaymentTxState.CREATED)
        succeed_payment(zyt.NAME, tx, payment_record)
    return payment_record


def is_payment_expired(record):
    from datetime import datetime

    if record.tried_times >= config.Biz.PAYMENT_MAX_TRIAL_TIMES:
        return True

    d = datetime.utcnow() - record.updated_on
    s = d.total_seconds()
    return s >= config.Biz.PAYMENT_MAX_VALID_SECONDS


@transactional
def _restart_payment(channel, payment_record, amount, product_name, product_category, product_desc):
    from ..utils import generate_sn

    tx = payment_record.tx
    if not in_to_pay_state(tx.state, exclude=[PaymentTxState.PAID_OUT]):
        raise AlreadyPaidError(payment_record.order_id)

    # 更新订单相关信息
    if tx.state in [PaymentTxState.CREATED, PaymentTxState.FAILED]:
        payment_record.amount = amount
        payment_record.product_name = product_name
        payment_record.product_category = product_category
        payment_record.product_desc = product_desc
        tx.comments = "在线支付-{0}".format(product_name)

    if tx.amount != amount or is_payment_expired(payment_record):
        tx.amount = amount
        # push old sn to stack.
        tx_sn_stack = TransactionSnStack(tx_id=tx.id, sn=tx.sn, generated_on=tx.updated_on, state=tx.state)
        db.session.add(tx_sn_stack)

        # new sn.
        tx.sn = generate_sn(payment_record.payer_id)
        payment_record.sn = tx.sn
        payment_record.tried_times = 0

    # 如果之前失败了，则从这里重新开始
    if tx.state == PaymentTxState.FAILED:
        tx.state = PaymentTxState.CREATED

    tx.tried_times += 1
    payment_record.tried_times += 1
    db.session.add(tx)
    db.session.add(payment_record)
    return payment_record


@transactional
def _create_payment(channel, payment_type, payer_id, payee_id, order_id,
                    product_name, product_category, product_desc, amount,
                    client_callback_url, client_notify_url):
    comments = "在线支付-{0}".format(product_name)
    user_ids = [user_roles.from_user(payer_id), user_roles.to_user(payee_id)]
    if payment_type == PaymentType.GUARANTEE:
        secure_user_id = get_system_account_user_id(SECURE_USER_NAME)
        user_ids.append(user_roles.guaranteed_by(secure_user_id))
    tx = create_transaction(channel.name, TransactionType.PAYMENT, amount, comments, user_ids, order_id=order_id)

    fields = {
        'tx_id': tx.id,
        'sn': tx.sn,
        'payer_id': payer_id,
        'payee_id': payee_id,
        'channel_id': channel.id,
        'order_id': order_id,
        'product_name': product_name,
        'product_category': product_category,
        'product_desc': product_desc,
        'amount': amount,
        'client_callback_url': client_callback_url,
        'client_notify_url': client_notify_url,
        'type': payment_type
    }

    payment_record = PaymentRecord(**fields)
    db.session.add(payment_record)

    return payment_record


@transactional
def succeed_paid_out(vas_name, tx, payment_record):
    event_id = bookkeeping(EventType.TRANSFER_OUT, tx.sn, payment_record.payer_id, vas_name,
                           payment_record.amount)
    transit_transaction_state(tx.id, PaymentTxState.CREATED, PaymentTxState.PAID_OUT, event_id)


def in_to_pay_state(state, exclude=None):
    # 等待支付状态
    if exclude and state in exclude:
        return False

    return state in [PaymentTxState.CREATED, PaymentTxState.FAILED, PaymentTxState.PAID_OUT]


@transactional
def succeed_payment(vas_name, tx, payment_record):
    if not in_to_pay_state(tx.state):
        raise TransactionStateError()
    if payment_record.amount == 0:
        # 不用记账
        event_id = None
    else:
        event_id = bookkeeping(EventType.TRANSFER_IN, tx.sn, payment_record.payee_id, vas_name,
                               payment_record.amount)
    transit_transaction_state(tx.id, tx.state, PaymentTxState.SUCCESS, event_id)


@transactional
def duplicate_payment_to_balance(vas_name, vas_sn, tx, payment_record):
    event_id = bookkeeping(EventType.TRANSFER_IN, tx.source_sn, payment_record.payer_id, vas_name,
                           payment_record.amount)
    # 不改变状态，只是添加一条关联event
    transit_transaction_state(tx.id, tx.state, tx.state, event_id)

    duplicate_payment_record = DuplicatedPaymentRecord(tx_id=tx.id,
                                                       sn=tx.sn, event_id=event_id, vas_name=vas_name, vas_sn=vas_sn,
                                                       source=TransactionType.PAYMENT)
    db.session.add(duplicate_payment_record)


@transactional
def secure_payment(vas_name, tx, payment_record):
    if not in_to_pay_state(tx.state):
        raise TransactionStateError()
    secure_user_id = get_system_account_user_id(SECURE_USER_NAME)
    event_id = bookkeeping(EventType.TRANSFER_IN_FROZEN, tx.sn, secure_user_id, vas_name,
                           payment_record.amount)
    transit_transaction_state(tx.id, tx.state, PaymentTxState.SECURED, event_id)


@transactional
def _confirm_payment(payment_record):
    secure_user_id = get_system_account_user_id(SECURE_USER_NAME)
    # 确认金额为订单金额 - 已退款金额
    amount = payment_record.amount - payment_record.refunded_amount
    event_id1 = zyt_bookkeeping(EventType.TRANSFER_OUT_FROZEN, payment_record.sn, secure_user_id, amount)
    event_id2 = zyt_bookkeeping(EventType.TRANSFER_IN, payment_record.sn, payment_record.payee_id, amount)

    transit_transaction_state(payment_record.tx_id, PaymentTxState.SECURED, PaymentTxState.SUCCESS,
                              [event_id1, event_id2])


@transactional
def fail_payment(payment_record):
    transit_transaction_state(payment_record.tx_id, PaymentTxState.CREATED, PaymentTxState.FAILED)


@transactional
def handle_paid_out(vas_name, sn, notify_handle=None):
    tx = get_payment_tx_by_sn(sn)
    succeed_paid_out(vas_name, tx, tx.record)

    if notify_handle is not None:
        notify_handle(True)


def handle_payment_result(is_success, sn, vas_name, vas_sn, data):
    """
    :param is_success: 是否成功
    :param sn: 订单号
    :param vas_name: 来源系统
    :param vas_sn: 来源系统订单号
    :param data: 数据
    :return:
    """
    tx = get_payment_tx_by_sn(sn)
    payment_record = tx.record
    client_callback_url = payment_record.client_callback_url

    req_code = 0 if is_success else 1
    code = 0 if tx.state not in [PaymentTxState.FAILED, PaymentTxState.CREATED] else 1
    if tx.state != PaymentTxState.CREATED and client_callback_url:
        # 必须要tx状态改变
        if code != req_code:
            logger.warn('callback result mismatch with notify result.')
            # 等待半秒钟
            time.sleep(0.5)
            code = 0 if tx.state not in [PaymentTxState.FAILED, PaymentTxState.CREATED] else 1
        from api_x.utils.notify import sign_and_return_client_callback
        user_mapping = get_user_map_by_account_user_id(payment_record.payer_id)
        user_id = user_mapping.user_id
        params = {'code': code, 'user_id': user_id, 'sn': payment_record.sn,
                  'order_id': payment_record.order_id, 'amount': payment_record.amount}
        return sign_and_return_client_callback(client_callback_url, tx.channel_name, params, method="POST")

    from flask import jsonify
    return jsonify(code=code, source=TransactionType.PAYMENT, sn=sn, vas_name=vas_name)


def handle_payment_notify(is_success, sn, vas_name, vas_sn, data):
    """
    :param is_success: 是否成功
    :param sn: 订单号
    :param vas_name: 来源系统
    :param vas_sn: 来源系统订单号
    :param data: 数据
    :return:
    """
    tx = get_payment_tx_by_sn(sn)
    payment_record = tx.record

    if is_duplicated_notify(tx, vas_name, vas_sn):
        return

    if _is_duplicated_payment(tx, vas_name, vas_sn):
        # 重复支付
        logger.warning('duplicated payment: [{0}, {1}], [{2}, {3}]'.format(tx.vas_name, tx.vas_sn, vas_name, vas_sn))
        if is_success:
            # 成功支付
            # FIXME, 暂时退款到余额，然后人工处理, 之后可能改成自动原路返回
            duplicate_payment_to_balance(vas_name, vas_sn, tx, payment_record)
        return

    with require_transaction_context():
        tx = update_transaction_info(tx.id, vas_sn, vas_name=vas_name)
        if is_success:
            # 直付和担保付的不同操作
            if payment_record.type == PaymentType.DIRECT:
                succeed_payment(vas_name, tx, payment_record)
            elif payment_record.type == PaymentType.GUARANTEE:
                secure_payment(vas_name, tx, payment_record)
        else:
            fail_payment(payment_record)

    # notify client.
    tx = get_tx_by_id(tx.id)
    _try_notify_client(tx, payment_record)


def _try_notify_client(tx, payment_record):
    from api_x.utils.notify import sign_and_notify_client

    url = payment_record.client_notify_url
    if not url:
        return

    user_mapping = get_user_map_by_account_user_id(payment_record.payer_id)
    user_id = user_mapping.user_id

    params = None
    if tx.state in [PaymentTxState.SECURED, PaymentTxState.SUCCESS]:
        params = {'code': 0, 'user_id': user_id, 'sn': payment_record.sn,
                  'order_id': payment_record.order_id, 'amount': payment_record.amount}
    elif tx.state == PaymentTxState.FAILED:
        params = {'code': 1, 'user_id': user_id, 'sn': payment_record.sn,
                  'order_id': payment_record.order_id, 'amount': payment_record.amount}

    # notify
    sign_and_notify_client(url, params, tx.channel_name, task=tasks.pay_notify)


def _is_duplicated_payment(tx, vas_name, vas_sn):
    if in_to_pay_state(tx.state):
        return False

    if tx.vas_name is None or tx.vas_sn is None:
        return False

    return vas_name != tx.vas_name or vas_sn != tx.vas_sn


def confirm_payment(channel, order_id):
    payment_record = get_payment_by_channel_order_id(channel.id, order_id)
    if payment_record is None or payment_record.type != PaymentType.GUARANTEE:
        raise TransactionNotFoundError('guarantee payment tx channel={0}, order_id={1} not found.'.format(channel.name, order_id))

    tx = get_tx_by_id(payment_record.tx_id)
    # 只有担保才能确认
    # 另外，担保可能发生退款的情况，则需要退款完成之后再次确认。
    if tx.state == PaymentTxState.SECURED:
        _confirm_payment(payment_record)
    elif tx.state == PaymentTxState.REFUNDING:
        msg = 'payment is REFUNDING, try again later.'
        logger.warn(msg)
        raise TransactionStateError(msg)
    else:
        logger.warn('payment state should be SECURED.')