# coding=utf-8
from api.constant import PaymentState
from api.payment import dba
from pytoolbox.util.dbe import db_transactional


@db_transactional
def refund_prepared(db, id):
    return dba.transit_state(db, id, PaymentState.SECURED, PaymentState.REFUND_PREPARED)


@db_transactional
def refund_canceled(db, id):
    return dba.transit_state(db, id, PaymentState.REFUND_PREPARED, PaymentState.SECURED)


@db_transactional
def refund_started(db, id):
    return dba.transit_state(db, id, PaymentState.REFUND_PREPARED, PaymentState.REFUNDING)


@db_transactional
def refund_ended(db, id, amount):
    if dba.set_refunded_amount(db, id, amount):
        return dba.transit_state(db, id, PaymentState.REFUNDING, PaymentState.SECURED)


def confirm(id):
    return dba.transit_state(id, PaymentState.SECURED, PaymentState.CONFIRMED)
