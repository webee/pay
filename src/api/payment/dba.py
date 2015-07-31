# coding=utf-8
from datetime import datetime, timedelta

from api.constant import PaymentState
from tools.dbe import db_context


@db_context
def set_refunded_amount(db, id, amount):
    return db.execute("""
                    UPDATE payment
                      SET refunded_amount=%(amount)s
                      WHERE id=%(id)s
    """, id=id, amount=amount) > 0


@db_context
def transit_state(db, id, prev_state, new_state):
    return db.execute("""
                    UPDATE payment
                      SET state=%(new_state)s, updated_on=%(updated_on)s
                      WHERE id=%(id)s AND state=%(prev_state)s
        """, id=id, prev_state=prev_state, new_state=new_state, updated_on=datetime.now()) > 0


@db_context
def create_payment(db, id, client_id, payer_account_id, payee_account_id, order, amount, callback_url,
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
    db.insert('payment', **payment_fields)


@db_context
def find_payment_by_id(db, id):
    return db.get('SELECT * FROM payment WHERE id = %(id)s', id=id)


@db_context
def find_payment_by_order_no(db, client_id, order_no):
    return db.get('SELECT * FROM payment WHERE client_id = %(client_id)s AND order_id=%(order_id)s',
                  client_id=client_id, order_id=order_no)


@db_context
def list_expired_payment(db):
    return db.list('SELECT * FROM payment WHERE state = %(state)s AND auto_confirm_expired_on < %(expired_on)s',
                          state=PaymentState.SECURED, expired_on=datetime.now())


@db_context
def succeed_payment(db, id, paybill_id):
    now = datetime.now()
    db.execute(
        """
            UPDATE payment
              SET state = %(new_state)s, transaction_ended_on = %(ended_on)s, paybill_id=%(paybill_id)s,
                  auto_confirm_expired_on=%(expired_on)s
              WHERE id = %(id)s
        """,
        id=id, new_state=PaymentState.SECURED, paybill_id=paybill_id, ended_on=now, expired_on=_few_days_later(now, 3))


@db_context
def fail_payment(db, id):
    db.execute('UPDATE payment SET state = %(new_state)s, transaction_ended_on = %(ended_on)s WHERE id = %(id)s',
                      id=id, new_state=PaymentState.FAILED, ended_on=datetime.now())


def _few_days_later(from_datetime, days):
    return from_datetime + timedelta(days=days)
