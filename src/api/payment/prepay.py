# -*- coding: utf-8 -*-
from datetime import datetime

from api.util import id
from api.util.ipay import transaction
from api.account.account import find_or_create_account
from tools.dbe import from_db, transactional


class Order(object):
    def __init__(self, no, name, desc, created_on):
        self.no = no
        self.name = name
        self.desc = desc
        self.created_on = created_on
        self.category = '虚拟商品'


@transactional
def generate_prepay_transaction(client_id, payer_user_id, payee_user_id, order, amount):
    payer_account_id = find_or_create_account(client_id, payer_user_id)
    payee_account_id = find_or_create_account(client_id, payee_user_id)

    payment_id = id.pay_id(payer_account_id)
    payment_fields = {
        'id': payment_id,
        'client_id': client_id,
        'order_id': order.no,
        'product_name': order.name,
        'product_category': order.category,
        'product_desc': order.desc,
        'payer_account_id': payer_account_id,
        'payee_account_id': payee_account_id,
        'amount': amount,
        'ordered_on': order.created_on,
        'callback_url': transaction.generate_pay_notification_url(payment_id),
        'created_on': datetime.now()
    }
    from_db().insert('payment', **payment_fields)

    return payment_id
