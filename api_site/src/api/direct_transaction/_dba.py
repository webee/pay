# -*- coding: utf-8 -*-
from datetime import datetime

from pytoolbox.util.enum import enum
from pytoolbox.util.dbe import db_context


PAYMENT_STATE = enum(CREATED='CREATED', SUCCESS='SUCCESS', FAILED='FAILED')


@db_context
def create_payment(db, _id, channel_id, payer_account_id, payee_account_id, order, amount,
                   client_callback_url, client_async_callback_url, created_on):
    payment_fields = {
        'id': _id,
        'channel_id': channel_id,
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
        'state': PAYMENT_STATE.CREATED,
        'created_on': created_on
    }
    db.insert('direct_payment', **payment_fields)


@db_context
def find_payment_by_id(db, id):
    return db.get('SELECT * FROM direct_payment WHERE id = %(id)s', id=id)


@db_context
def find_payment_by_order_no(db, channel_id, order_no):
    return db.get('SELECT * FROM direct_payment WHERE channel_id = %(channel_id)s AND order_id=%(order_id)s',
                  channel_id=channel_id, order_id=order_no)


@db_context
def update_payment_state(db, _id, state):
    return db.execute(
        """
            UPDATE direct_payment SET state = %(state)s, updated_on = %(updated_on)s
              WHERE id = %(id)s
        """, id=_id, state=state, updated_on=datetime.now())
