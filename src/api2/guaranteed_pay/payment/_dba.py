# -*- coding: utf-8 -*-
from datetime import datetime

from ..util import oid
from api2.util.enum import enum
from pytoolbox.util.dbe import db_context


PAYMENT_STATE = enum(CREATED='CREATED', SECURED='SECURED', FAILED='FAILED', CONFIRMED='CONFIRMED', REFUNDED='REFUNDED')


@db_context
def create_payment(db, id, channel_id, payer_account_id, payee_account_id, order, amount,
                   client_callback_url, client_async_callback_url, created_on):
    payment_fields = {
        'id': id,
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
def find_payment_by_id(db, id):
    return db.get('SELECT * FROM guaranteed_payment WHERE id = %(id)s', id=id)


@db_context
def find_payment_by_order_no(db, channel_id, order_no):
    return db.get('SELECT * FROM guaranteed_payment WHERE channel_id = %(channel_id)s AND order_id=%(order_id)s',
                  channel_id=channel_id, order_id=order_no)


@db_context
def find_secured_account_id(db, client_id):
    return db.get_scalar('SELECT account_id FROM secured_account WHERE client_id = %(client_id)s',
                         client_id)


@db_context
def cache_secured_account_id(db, client_id, account_id):
    fields = {
        'client_id': client_id,
        'account_id': account_id,
        'created_on': datetime.now()
    }
    db.insert('payment_group', **fields)


@db_context
def update_payment_state(db, _id, state):
    return db.execute(
        """
            UPDATE guaranteed_payment SET state = %(state)s, updated_on = %(updated_on)s
              WHERE id = %(id)s
        """, id=_id, state=state, updated_on=datetime.now())


@db_context
def secure_payment(db, payment_id, payer_account_id, amount):
    _id = oid.secured_pay_id(payer_account_id)
    fields = {
        'id': _id,
        'guaranteed_payment_id': payment_id,
        'payer_account_id': payer_account_id,
        'amount': amount,
        'created_on': datetime.now()
    }
    db.insert('secure_payment', **fields)
    return _id


@db_context
def confirm_to_pay(db, payment_id, payee_account_id, amount):
    _id = oid.confirmed_pay_id(payee_account_id)
    fields = {
        'id': _id,
        'guaranteed_payment_id': payment_id,
        'payee_account_id': payee_account_id,
        'amount': amount,
        'created_on': datetime.now()
    }
    db.insert('confirm_payment', **fields)
    return _id