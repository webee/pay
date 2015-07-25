# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from tools.dbe import from_db
from api.constant import PaymentState


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
    return from_db().get_scalar('SELECT amount FROM payment WHERE id = %(id)s', id=id)


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
