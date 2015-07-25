# coding=utf-8
from api.constant import PaymentState
from api.payment import dba
from tools.dbe import db_transactional


@db_transactional
def refund_started(db, id, state):
    # state -> [SECURED, REFUNDED, REFUND_FAILED]
    return dba.transit_state(db, id, state, PaymentState.REFUNDING)


@db_transactional
def refund_ended(db, id, amount):
    if dba.set_refunded_amount(db, id, amount):
        return dba.transit_state(db, id, PaymentState.REFUNDING, PaymentState.SECURED)


def confirm(id):
    return dba.transit_state(id, PaymentState.SUCCESS, PaymentState.CONFIRMED)