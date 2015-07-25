# -*- coding: utf-8 -*-
from datetime import datetime

from decimal import Decimal
from api.constant import SourceType, RefundStep
from api.payment import payment
from api.refund.error import NoPaymentFoundError, RefundFailedError, PaymentStateMissMatchError, RefundAmountError
from api.util.bookkeeping import bookkeeping, Event
from api.util.ipay import transaction
from api.util.ipay.error import ApiError
from api.util.ipay.transaction import notification
from tools.dbe import from_db, db_operate, transactional, db_transactional
from api.constant import PayState, RefundState
from top_config import lianlian
from . import refund_db


def apply_for_refund(client_id, order_id, amount, callback_url):
    payment_order = _get_payment_to_refund(client_id, order_id)
    if amount >= payment_order.amount or amount <= 0:
        raise RefundAmountError(amount)

    refund_order = _create_refund_freezing(payment_order, amount, callback_url)

    _request_refund(payment_order, refund_order)

    return refund_order.id


def handle_refund_result(refund_id, data):
    sta_refund = data['sta_refund']
    oid_refundno = data['oid_refundno']
    amount = Decimal(data['money_refund'])

    refund_order = refund_db.get_refund(refund_id)
    if refund_order.state != RefundState.FROZEN:
        return notification.duplicate()

    if refund_order.amount != amount:
        return notification.is_invalid()

    _set_refund_info(refund_id, oid_refundno)

    if sta_refund == lianlian.Refund.Status.FAILED:
        _fail_refund(refund_id)
    elif sta_refund == lianlian.Refund.Status.SUCCESS:
        _succeed_refund(refund_order)
    return notification.succeed()


def query_refund(refund_id):
    return refund_db.get_refund(refund_id)


@transactional
def _fail_refund(refund_order):
    payment.refund_failed(refund_order.payment_id)

    _unfrozen_back_refund(refund_order)


@db_transactional
def _succeed_refund(db, refund_order):
    payment.refund_success(db, refund_order.payment_id, refund_order.amount)

    _unfrozen_out_refund(refund_order)


def _get_payment_to_refund(client_id, order_id):
    payment_order = refund_db.get_payment(client_id, order_id)
    if not payment_order:
        raise NoPaymentFoundError(client_id, order_id)
    if payment_order.state != PayState.SECURED:
        raise PaymentStateMissMatchError()
    return payment_order


@transactional
def _create_refund_freezing(payment_order, amount, callback_url):
    payment_id = payment_order.id
    payer_account_id = payment_order.payer_account_id
    payee_account_id = payment_order.payee_account_id

    if not payment.refund_started(payment_id):
        raise RefundFailedError()

    refund_order = refund_db.create_refund(payment_id, payer_account_id, payee_account_id, amount, callback_url)
    _frozen_refund(refund_order)

    return refund_order


def _request_refund(payment_order, refund_order):
    refund_id = refund_order.id
    created_on = refund_order.created_on
    amount = refund_order.amount
    paybill_id = payment_order.paybill_id
    try:
        res = transaction.refund(refund_id, created_on, amount, paybill_id)
    except ApiError:
        _refund_request_failed(refund_order)
        raise RefundFailedError()

    if 'oid_refundno' in res:
        oid_refundno = res['oid_refundno']
        _set_refund_info(refund_id, oid_refundno)


@transactional
def _refund_request_failed(payment_id, refund_id):
    payment.refund_failed(payment_id)
    _transit_refund_failed(refund_id)

    refund_order = refund_db.get_refund(refund_id)
    _unfrozen_back_refund(refund_order)


@db_operate
def _set_refund_info(db, refund_id, refund_serial_no):
    return db.execute("""
            UPDATE refund
                SET refund_serial_no=%(refund_serial_no)s, updated_on=%(updated_on)
                WHERE id=%(id)s
        """, id=refund_id, refund_serial_no=refund_serial_no, updated_on=datetime.now()) > 0


def _find_refund(client_id, refund_id):
    return from_db().get(
        """
            SELECT *
              FROM refund
              WHERE client_id = %(client_id)s AND id = %(id)s
        """,
        client_id=client_id, id=refund_id)


## refund events.
def _frozen_refund(refund_order):
    bookkeeping(
        Event(refund_order.payee_account_id, SourceType.REFUND, RefundStep.FROZEN,
              refund_order.id, refund_order.amount),
        '-secured', '+frozen'
    )


def _unfrozen_back_refund(refund_order):
    bookkeeping(
        Event(refund_order.payee_account_id, SourceType.REFUND, RefundStep.FAILED,
              refund_order.id, refund_order.amount),
        '-frozen', '+secured'
    )


def _unfrozen_out_refund(refund_order):
    bookkeeping(
        Event(refund_order.payee_account_id, SourceType.REFUND, RefundStep.SUCCESS,
              refund_order.id, refund_order.amount),
        '-frozen', '-asset'
    )


## refund state transition.
def _transit_refund_failed(id):
    return refund_db.transit_state(id, RefundState.FROZEN, RefundState.FAILED)


def _transit_refund_success(id):
    return refund_db.transit_state(id, RefundState.FROZEN, RefundState.SUCCESS)
