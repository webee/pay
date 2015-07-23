# -*- coding: utf-8 -*-
from datetime import datetime

from api.util.enum import enum
from tools.dbe import from_db


PaymentState = enum(CREATED='CREATED')


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