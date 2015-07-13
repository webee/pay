# -*- coding: utf-8 -*-
from tools.dbi import from_db, transactional
from . import config


class Order(object):
    def __init__(self, no, name, desc, created_on):
        self.no = no
        self.name = name
        self.desc = desc
        self.created_on = created_on
        self.category = '虚拟商品'


@transactional
def generate_prepay_order(client_id, payer_user_id, payee_user_id, order, amount, notification_url):
    payer_account_id = _find_or_create_account(client_id, payer_user_id)
    payee_account_id = _find_or_create_account(client_id, payee_user_id)

    payment_fields = {
        'id': _generate_transaction_id(payer_account_id),
        'client_id': client_id,
        'order_id': order.no,
        'product_name': order.name,
        'product_category': order.category,
        'product_desc': order.desc,
        'payer_account_id': payer_account_id,
        'payee_account_id': payee_account_id,
        'amount': amount,
        'callback_url': notification_url
    }
    from_db().insert('payment', **payment_fields)


def build_pay_url(pay_id):
    pass


def _generate_transaction_id(payer_account_id):
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d%H%M%S%f") + '%0.7d' % payer_account_id


def _find_or_create_account(client_id, user_id):
    account_id = from_db().get_scalar('SELECT id FROM account WHERE client_id = %(client_id)s AND user_id = %(user_id)s',
                                      client_id=client_id, user_id=user_id)
    if not account_id:
        fields = {
            'client_id': client_id,
            'user_id': user_id
        }
        account_id = from_db().insert('account', returns_id=True, **fields)
    return account_id
