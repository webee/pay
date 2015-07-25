# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from api.payment.payment_db import transit_state
from api.util.enum import enum
from tools.dbe import from_db, db_transactional
from api.constant import PayState
from . import payment_db

PaymentState = enum(CREATED='CREATED', SUCCESS='SUCCESS', FAILED='FAILED', CONFIRMED='CONFIRMED',
                    REFUNDING='REFUNDING', REFUNDED='REFUNDED', REFUND_FAILED='REFUND_FAILED')


def create(id, client_id, payer_account_id, payee_account_id, order, amount, callback_url,
           client_callback_url):
    payment_fields = {
        'id': id,
        'client_id': client_id,
        'order_id': order.no,
        'product_name': order.name,
        'product_category': order.category,
        'product_desc': order.desc,
        'payer_account_id': payer_account_id,
        'payee_account_id': payee_account_id,
        'amount': amount,
        'ordered_on': order.created_on,
        'callback_url': callback_url,
        'client_callback_url': client_callback_url,
        'state': PaymentState.CREATED,
        'created_on': datetime.now()
    }
    from_db().insert('payment', **payment_fields)


def find(id):
    return from_db().get('SELECT * FROM payment WHERE id = %(id)s', id=id)


def get_amount(id):
    return from_db().get_scalar('SELECT amount FROM payment WHERE id = %(id)s AND success IS NULL', id=id)


def list_expired():
    return from_db().list('SELECT * FROM payment WHERE state = %(state)s AND auto_confirm_expired_on < %(expired_on)s',
                          state=PaymentState.SUCCESS, expired_on=datetime.now()
                          )


def succeed(id, paybill_id):
    now = datetime.now()
    from_db().execute(
        """
            UPDATE payment
              SET state = %(new_state)s, transaction_ended_on = %(ended_on)s, paybill_id=%(paybill_id)s,
                  auto_confirm_expired_on=%(expired_on)s
              WHERE id = %(id)s
        """,
        id=id, new_state=PaymentState.SUCCESS, paybill_id=paybill_id, ended_on=now, expired_on=_few_days_later(now, 3))


def fail(id):
    from_db().execute('UPDATE payment SET state = %(new_state)s, transaction_ended_on = %(ended_on)s WHERE id = %(id)s',
                      id=id, new_state=PaymentState.FAILED, ended_on=datetime.now())


def _few_days_later(from_datetime, days):
    return from_datetime + timedelta(days=days)


def confirm(id):
    return payment_db.transit_state(id, PaymentState.SUCCESS, PaymentState.CONFIRMED)


def refund_started(id):
    return payment_db.transit_state(id, PayState.SECURED, PayState.REFUNDING)


def refund_failed(id):
    return payment_db.transit_state(id, PaymentState.REFUNDING, PaymentState.REFUND_FAILED)


@db_transactional
def refund_success(db, id, amount):
    payment_db.set_refunded_amount(db, id, amount)
    return payment_db.transit_state(db, id, PaymentState.REFUNDING, PaymentState.REFUNDED)
