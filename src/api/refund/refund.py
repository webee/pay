# -*- coding: utf-8 -*-

from decimal import Decimal, InvalidOperation
from contextlib import contextmanager

from api.util.error import AmountValueError, NegativeAmountError
from api.refund.error import NoPaymentFoundError, RefundFailedError, PaymentStateMissMatchError, RefundAmountError
from api.refund.dba import set_refund_info
from api.refund import transit
from api.util.ipay import transaction
from api.util.ipay.error import ApiError
from api.util.ipay.transaction import notification
from pytoolbox.util.dbe import transactional, db_transactional
from tools.lock import GetLockError, GetLockTimeoutError, require_order_lock
from tools.mylog import get_logger
from api.constant import PaymentState, RefundState
from pytoolbox import config
from api.payment import transit as payment_transit
from . import dba
from . import notify


logger = get_logger(__name__)

_REFUND_STATUS_SUCCESS = config.get('lianlianpay', 'refund_status_success')
_REFUND_STATUS_FAILED = config.get('lianlianpay', 'refund_status_failed')


@contextmanager
def require_lock_payment_order(client_id, order_id):
    try:
        with require_order_lock('{0}.{1}'.format(client_id, order_id)) as lock:
            yield lock
    except GetLockError as e:
        raise RefundFailedError(e.message)
    except GetLockTimeoutError as e:
        raise RefundFailedError(e.message)


def prepare(client_id, order_id):
    with require_lock_payment_order(client_id, order_id):
        payment_order = _get_payment_to_prepare_refund(client_id, order_id)
        if payment_order.state == PaymentState.REFUND_PREPARED:
            return True

        return payment_transit.refund_prepared(payment_order.id)


def cancel(client_id, order_id):
    with require_lock_payment_order(client_id, order_id):
        payment_order = _get_payment_to_cancel_refund(client_id, order_id)

        return payment_transit.refund_canceled(payment_order.id)


def apply_for_refund(client_id, order_id, amount, callback_url):
    with require_lock_payment_order(client_id, order_id):
        payment_order = _get_payment_to_start_refund(client_id, order_id)

        try:
            amount_value = Decimal(amount)
        except InvalidOperation:
            raise AmountValueError(amount)
        if amount_value <= 0:
            raise NegativeAmountError(amount_value)

        if amount_value + payment_order.refunded_amount > payment_order.amount:
            raise RefundAmountError(amount)

        refund_order = _create_refund_freezing(payment_order, amount, callback_url)

    _request_refund(payment_order, refund_order)

    return refund_order.id


def handle_refund_notify(refund_id, data):
    amount = Decimal(data['money_refund'])

    refund_order = dba.get_refund(refund_id)
    if refund_order is None:
        return notification.is_invalid()
    elif refund_order.state != RefundState.FROZEN:
        return notification.duplicate()
    elif refund_order.amount != amount:
        return notification.is_invalid()

    sta_refund = data['sta_refund']
    oid_refundno = data['oid_refundno']
    if _process_refund_result(refund_order, oid_refundno, sta_refund):
        notify.try_notify_client(refund_id)
        return notification.accepted()
    return notification.refused()


def query_refund(refund_id):
    return dba.get_refund(refund_id)


@transactional
def _process_refund_result(refund_order, oid_refundno, status):
    set_refund_info(refund_order.id, oid_refundno)

    # process refund status.
    if status == _REFUND_STATUS_FAILED:
        transit.refund_failed(refund_order)
    elif status == _REFUND_STATUS_SUCCESS:
        transit.refund_success(refund_order)
    else:
        logger.warn("refund notify result: [{0}], id=[{1}]".format(status, refund_order.id))
        return False
    return True


@transactional
def _process_request_failure(refund_order):
    transit.refund_failed(refund_order)


@db_transactional
def _create_refund_freezing(db, payment_order, amount, callback_url):
    if payment_order.state == PaymentState.SECURED:
        payment_transit.refund_prepared(db, payment_order.id)

    payment_id = payment_order.id
    payer_account_id = payment_order.payer_account_id
    payee_account_id = payment_order.payee_account_id

    refund_id = dba.create_refund(db, payment_id, payer_account_id, payee_account_id, amount, callback_url)
    refund_order = dba.get_refund(db, refund_id)
    if not transit.refund_frozen(db, refund_order):
        raise RefundFailedError()

    return refund_order


def _request_refund(payment_order, refund_order):
    refund_id = refund_order.id
    created_on = refund_order.created_on
    amount = refund_order.amount
    paybill_id = payment_order.paybill_id
    try:
        res = transaction.refund(refund_id, created_on, amount, paybill_id)

        if 'oid_refundno' in res:
            oid_refundno = res['oid_refundno']
            set_refund_info(refund_id, oid_refundno)
    except (ApiError, Exception) as e:
        _process_request_failure(refund_order)
        raise RefundFailedError(e.message)


def _get_payment_to_refund(client_id, order_id):
    payment_order = dba.get_payment(client_id, order_id)
    if not payment_order:
        raise NoPaymentFoundError(client_id, order_id)
    return payment_order


def _get_payment_to_start_refund(client_id, order_id):
    payment_order = _get_payment_to_refund(client_id, order_id)
    if payment_order.state not in [PaymentState.REFUND_PREPARED, PaymentState.SECURED]:
        raise PaymentStateMissMatchError()
    return payment_order


def _get_payment_to_prepare_refund(client_id, order_id):
    payment_order = _get_payment_to_refund(client_id, order_id)
    if payment_order.state not in [PaymentState.SECURED, PaymentState.REFUND_PREPARED]:
        raise PaymentStateMissMatchError()
    return payment_order


def _get_payment_to_cancel_refund(client_id, order_id):
    payment_order = _get_payment_to_refund(client_id, order_id)
    if payment_order.state != PaymentState.REFUND_PREPARED:
        raise PaymentStateMissMatchError()
    return payment_order
