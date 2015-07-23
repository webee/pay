# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from api.util.enum import enum

from tools.dbe import from_db

PaymentState = enum(CREATED='CREATED', SUCCESS='SUCCESS', FAILED='FAILED', CONFIRMED='CONFIRMED')


def create(id, client_id, payer_account_id, payee_account_id, order, amount, callback_url,
           client_return_url_when_succeed):
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
        'client_success_return_url': client_return_url_when_succeed,
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


def confirm(id):
    rowcount = from_db().execute(
        """
          UPDATE payment SET state=%(new_state)s, confirmed_on=%(confirmed_on)s
            WHERE id=%(id)s AND state=%(prev_state)s
        """,
        id=id, prev_state=PaymentState.SUCCESS, new_state=PaymentState.CONFIRMED, confirmed_on=datetime.now()
    )
    return rowcount > 0


def _few_days_later(from_datetime, days):
    return from_datetime + timedelta(days=days)
