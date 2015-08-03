# -*- coding: utf-8 -*-

from api2.guaranteed_pay.constant import PaymentState
from pytoolbox.util.dbe import db_context


@db_context
def create_payment(db, id, client_id, payer_account_id, payee_account_id, order, amount,
                   client_callback_url, client_async_callback_url, created_on):
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
        'client_callback_url': client_callback_url,
        'client_async_callback_url': client_async_callback_url,
        'state': PaymentState.CREATED,
        'created_on': created_on
    }
    db.insert('guaranteed_payment', **payment_fields)


@db_context
def group_payment(db, group_id, payment_id, created_on):
    fields = {
        'group_id': group_id,
        'payment_id': payment_id,
        'created_on': created_on
    }
    db.insert('payment_group', **fields)


@db_context
def find_payment_by_order_no(db, client_id, order_no):
    return db.get('SELECT * FROM payment WHERE client_id = %(client_id)s AND order_id=%(order_id)s',
                  client_id=client_id, order_id=order_no)
