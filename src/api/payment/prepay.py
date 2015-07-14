# -*- coding: utf-8 -*-
from datetime import datetime
from urlparse import urljoin

from api.util.uuid import encode_uuid
from api.account.account import find_or_create_account
from tools.dbi import from_db, transactional


class Order(object):
    def __init__(self, no, name, desc, created_on):
        self.no = no
        self.name = name
        self.desc = desc
        self.created_on = created_on
        self.category = '虚拟商品'


@transactional
def generate_prepay_transaction(client_id, payer_user_id, payee_user_id, order, amount, request_root, notification_url):
    payer_account_id = find_or_create_account(client_id, payer_user_id)
    payee_account_id = find_or_create_account(client_id, payee_user_id)

    transaction_id = _generate_transaction_id(payer_account_id)
    uuid = encode_uuid(transaction_id)
    payment_fields = {
        'id': transaction_id,
        'client_id': client_id,
        'order_id': order.no,
        'product_name': order.name,
        'product_category': order.category,
        'product_desc': order.desc,
        'payer_account_id': payer_account_id,
        'payee_account_id': payee_account_id,
        'amount': amount,
        'ordered_on': order.created_on,
        'callback_url': _generate_notification_url(request_root, notification_url, uuid),
        'created_on': datetime.now()
    }
    from_db().insert('payment', **payment_fields)

    return uuid


def _generate_transaction_id(payer_account_id):
    return datetime.now().strftime("%Y%m%d%H%M%S%f") + '%0.7d' % payer_account_id


def _generate_notification_url(url_root, relative_url, uuid):
    params = {'uuid': uuid}
    relative_url = relative_url.format(**params)
    return urljoin(url_root, relative_url)
