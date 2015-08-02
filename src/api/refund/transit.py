# coding=utf-8
from pytoolbox.util.dbe import db_transactional
from api.constant import RefundState
from api.payment import transit as payment_transit
from . import dba
from . import event


@db_transactional
def refund_frozen(db, refund_order):
    if payment_transit.refund_started(db, refund_order.payment_id):
        if dba.transit_state(db, refund_order.id, RefundState.FROZEN, RefundState.FROZEN):
            return event.frozen(refund_order.payee_account_id, refund_order.id, refund_order.amount)


@db_transactional
def refund_failed(db, refund_order):
    if payment_transit.refund_ended(db, refund_order.payment_id):
        if dba.transit_state(db, refund_order.id, RefundState.FROZEN, RefundState.FAILED):
            return event.unfrozen_back(refund_order.payee_account_id, refund_order.id, refund_order.amount)


@db_transactional
def refund_success(db, refund_order):
    if payment_transit.refund_ended(db, refund_order.payment_id, refund_order.amount):
        if dba.transit_state(db, refund_order.id, RefundState.FROZEN, RefundState.SUCCESS):
            return event.unfrozen_out(refund_order.payee_account_id, refund_order.id, refund_order.amount)
