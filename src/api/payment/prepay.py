# -*- coding: utf-8 -*-
from . import payment
from api.util import id
from api.util.ipay import transaction
from api.account.account import find_or_create_account
from tools.dbe import transactional


class Order(object):
    def __init__(self, no, name, desc, created_on):
        self.no = no
        self.name = name
        self.desc = desc
        self.created_on = created_on
        self.category = '虚拟商品'


@transactional
def generate_prepay_transaction(client_id, payer_user_id, payee_user_id, order, amount, client_success_return_url):
    payer_account_id = find_or_create_account(client_id, payer_user_id)
    payee_account_id = find_or_create_account(client_id, payee_user_id)

    payment_id = id.pay_id(payer_account_id)
    callback_url = transaction.generate_pay_notification_url(payment_id),
    payment.create(payment_id, client_id, payer_account_id, payee_account_id, order, amount, callback_url,
                   client_success_return_url)

    return payment_id
