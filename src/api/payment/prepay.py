# -*- coding: utf-8 -*-
from datetime import datetime

from .dba import create_payment, group_payment, find_payment_by_order_no
from api.util import oid
from api.util.ipay import transaction
from api.account.account import find_or_create_account
from pytoolbox.util.dbe import transactional


class Order(object):
    def __init__(self, activity_id, no, name, desc, created_on):
        self.activity_id = activity_id
        self.no = no
        self.name = name
        self.desc = desc
        self.created_on = created_on
        self.category = '虚拟商品'


@transactional
def find_or_create_prepay_transaction(client_id, payer_user_id, payee_user_id, order, amount,
                                      client_callback_url, client_async_callback_url):
    payer_account_id = find_or_create_account(client_id, payer_user_id)
    payee_account_id = find_or_create_account(client_id, payee_user_id)

    pay_record = find_payment_by_order_no(client_id, order.no)
    if pay_record:
        return pay_record['id']
    return _new_payment(amount, client_callback_url, client_async_callback_url,
                        client_id, order, payee_account_id, payer_account_id)


def _new_payment(amount, client_callback_url, client_async_callback_url,
                 client_id, order, payee_account_id, payer_account_id):
    payment_id = oid.pay_id(payer_account_id)
    callback_url = transaction.generate_pay_notification_url(payment_id)
    created_on = datetime.now()

    create_payment(payment_id, client_id, payer_account_id, payee_account_id, order, amount, callback_url,
                   client_callback_url, client_async_callback_url, created_on)
    group_payment(order.activity_id, payment_id, created_on)

    return payment_id
