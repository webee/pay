# coding=utf-8
from __future__ import unicode_literals
from decimal import InvalidOperation, Decimal

from api_x import db
from api_x.zyt.biz.refund.dba import update_payment_refunded_amount, update_refund_info
from api_x.zyt.vas.bookkeep import bookkeeping
from api_x.zyt.user_mapping import get_system_account_user_id
from api_x.constant import SECURE_USER_NAME, PaymentTransactionState, RefundTransactionState
from api_x.dbs import transactional
from ...vas.models import EventType
from ..transaction import create_transaction, transit_transaction_state, get_tx_by_sn, get_tx_by_id
from ..models import TransactionType, RefundRecord, PaymentType
from .error import *
from ..payment import get_payment_by_id, get_payment_by_sn
from api_x.utils.error import *
from .dba import get_tx_refund_by_sn


def apply_to_refund(channel_id, order_id, amount, client_notify_url):
    tx, payment_record = _get_tx_payment_to_refund(channel_id, order_id)

    try:
        amount_value = Decimal(amount)
    except InvalidOperation:
        raise AmountValueError(amount)
    if amount_value <= 0:
        raise NegativeAmountError(amount_value)

    refund_record = _create_and_request_refund(tx, payment_record, amount_value, client_notify_url)

    return refund_record


def handle_refund_notify(is_success, sn, vas_name, vas_sn, data):
    """
    :param is_success: 是否成功
    :param sn: 订单号
    :param vas_name: 来源系统
    :param vas_sn: 来源系统订单号
    :param data: 数据
    :return:
    """
    tx, refund_record = get_tx_refund_by_sn(sn)
    refund_record = update_refund_info(refund_record.id, vas_sn)
    payment_record = get_payment_by_sn(refund_record.payment_sn)

    if payment_record.state != PaymentTransactionState.REFUNDING:
        raise Exception('payment state error.')

    if is_success:
        # 直付和担保付的不同操作
        if payment_record.type == PaymentType.DIRECT:
            succeed_refund(vas_name, payment_record)
        elif payment_record.type == PaymentType.GUARANTEE:
            succeed_refund_secured(vas_name, payment_record)
    else:
        fail_refund(payment_record, refund_record)

    # TODO
    # notify

    return True


def _get_tx_payment_to_refund(channel_id, order_id):
    from ..payment import get_payment_by_channel_order_id

    payment_record = get_payment_by_channel_order_id(channel_id, order_id)
    if not payment_record:
        raise NoPaymentFoundError(channel_id, order_id)

    tx = get_tx_by_sn(payment_record.sn)
    if tx.state == PaymentTransactionState.REFUNDING:
        raise PaymentIsRefundingError()
    if not _is_refundable(tx, payment_record):
        raise PaymentNotRefundableError()
    return tx, payment_record


def _is_refundable(tx, payment_record):
    pay_type = payment_record.type
    if pay_type == PaymentType.DIRECT:
        return tx.state in [PaymentTransactionState.SUCCESS, PaymentTransactionState.REFUNDED]
    if pay_type == PaymentType.GUARANTEE:
        return tx.state in [PaymentTransactionState.SECURED, PaymentTransactionState.REFUNDED]

@transactional
def _create_and_request_refund(tx, payment_record, amount, client_notify_url):
    payment_record, refund_record = _create_refund(tx, payment_record, amount, client_notify_url)

    _request_refund(payment_record, refund_record)

    return refund_record


@transactional
def _create_refund(tx, payment_record, amount, client_notify_url):
    cur_payment_state = tx.state

    # start refunding.
    transit_transaction_state(tx.id, tx.state, PaymentTransactionState.REFUNDING)

    tx = get_tx_by_id(tx.id)
    payment_record = get_payment_by_id(payment_record.id)
    if tx.state != PaymentTransactionState.REFUNDING:
        raise PaymentNotRefundableError()

    if amount + payment_record.refunded_amount > payment_record.amount:
        raise RefundAmountError(amount)

    comments = "退款-交易流水号: [{0}]".format(payment_record.sn)

    user_ids = [payment_record.payer_id, payment_record.payee_id]
    if payment_record.type == PaymentType.GUARANTEE:
        secure_user_id = get_system_account_user_id(SECURE_USER_NAME)
        user_ids.append(secure_user_id)
    tx_record = create_transaction(TransactionType.REFUND, amount, comments, user_ids)

    fields = {
        'tx_id': tx_record.id,
        'sn': tx_record.sn,
        'payment_sn': payment_record.sn,
        'payment_state': cur_payment_state,
        'payer_id': payment_record.payer_id,
        'payee_id': payment_record.payee_id,
        'amount': amount,
        'vas_name': payment_record.vas_name,
        'client_notify_url': client_notify_url
    }

    refund_record = RefundRecord(**fields)
    db.session.add(refund_record)

    return payment_record, refund_record


def _request_refund(payment_record, refund_record):
    from api_x.zyt.evas import test_pay, lianlian_pay

    vas_name = payment_record.vas_name

    if vas_name == test_pay.NAME:
        raise RefundFailedError('vas {0} do not support refund now.'.format(vas_name))
    if vas_name == lianlian_pay.NAME:
        return _refund_by_lianlian_pay(payment_record, refund_record)
    raise RefundFailedError('unknown vas {0}'.format(vas_name))


def _refund_by_lianlian_pay(payment_record, refund_record):
    """连连退款"""
    from api_x.zyt.evas.lianlian_pay.error import ApiError
    from api_x.zyt.evas.lianlian_pay import refund

    vas_sn = payment_record.vas_sn

    sn = refund_record.sn
    created_on = refund_record.created_on
    amount = refund_record.amount
    try:
        res = refund(TransactionType.REFUND, sn, created_on, amount, vas_sn)

        if 'oid_refundno' in res:
            oid_refundno = res['oid_refundno']

            update_refund_info(refund_record.id, oid_refundno)
        return res
    except (ApiError, Exception) as e:
        fail_refund(payment_record, refund_record)
        raise RefundFailedError(e.message)


@transactional
def succeed_refund(vas_name, payment_record, refund_record):
    event_id = bookkeeping(EventType.TRANSFER_OUT, refund_record.sn, refund_record.payee_id, vas_name,
                           refund_record.amount)
    transit_transaction_state(payment_record.tx_id, PaymentTransactionState.REFUNDING,
                              refund_record.payment_state, event_id)
    transit_transaction_state(refund_record.tx_id, RefundTransactionState.CREATED,
                              RefundTransactionState.SUCCESS, event_id)

    update_payment_refunded_amount(payment_record.id, refund_record.amount)


@transactional
def succeed_refund_secured(vas_name, payment_record, refund_record):
    secure_user_id = get_system_account_user_id(SECURE_USER_NAME)
    event_id = bookkeeping(EventType.TRANSFER_OUT_FROZEN, payment_record.sn, secure_user_id, vas_name,
                           payment_record.amount)
    transit_transaction_state(payment_record.tx_id, PaymentTransactionState.REFUNDING,
                              refund_record.payment_state, event_id)
    transit_transaction_state(refund_record.tx_id, RefundTransactionState.CREATED,
                              RefundTransactionState.SUCCESS, event_id)

    update_payment_refunded_amount(payment_record.id, refund_record.amount)


@transactional
def fail_refund(payment_record, refund_record):
    transit_transaction_state(payment_record.tx_id, PaymentTransactionState.REFUNDING, refund_record.payment_state)
    transit_transaction_state(refund_record.tx_id, RefundTransactionState.CREATED, RefundTransactionState.FAILED)
