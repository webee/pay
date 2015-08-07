# -*- coding: utf-8 -*-
from datetime import datetime

from ._dba import find_payment_by_order_no, create_payment, find_payment_by_id
from .util import oid
from api.account import find_or_create_account, find_user_domain_id_by_channel, get_account_by_id, \
    get_secured_account_id
from api.core import pay as core_pay
from api.util import req
from pytoolbox.util.dbe import transactional


class Order(object):
    def __init__(self, activity_id, no, name, desc, created_on):
        self.activity_id = activity_id
        self.no = no
        self.name = name
        self.desc = desc
        self.created_on = created_on
        self.category = '虚拟商品'


class CorePayError(Exception):
    def __init__(self, payment_id):
        message = "Cannot pay[secured_payment_id={0}] to guaranteed account.".format(payment_id)
        super(CorePayError, self).__init__(message)


@transactional
def find_or_create_pay_transaction(channel_id, payer_user_id, payee_user_id, order, amount,
                                      client_callback_url, client_async_callback_url):
    user_domain_id = find_user_domain_id_by_channel(channel_id)
    payer_account_id = find_or_create_account(user_domain_id, payer_user_id)
    payee_account_id = find_or_create_account(user_domain_id, payee_user_id)

    pay_record = find_payment_by_order_no(channel_id, order.no)
    if pay_record:
        return pay_record['id']
    return _new_payment(amount, client_callback_url, client_async_callback_url,
                        channel_id, order, payee_account_id, payer_account_id)


def pay_by_id(payment_id):
    pay_record = find_payment_by_id(payment_id)

    payer_account_id = pay_record['payer_account_id']
    payer = get_account_by_id(payer_account_id)
    secured_account_id = get_secured_account_id()
    amount = pay_record['amount']
    pay_form = core_pay(
        trade_id=payment_id,
        payer_account_id=payer_account_id,
        payer_created_on=payer['created_on'],
        payee_account_id=secured_account_id,
        request_from_ip=req.ip(),
        product_name=pay_record['product_name'],
        product_desc=pay_record['product_desc'],
        traded_on=pay_record['ordered_on'],
        amount=amount
    )
    if not pay_form:
        raise CorePayError(payment_id)

    return pay_form


def _new_payment(amount, client_callback_url, client_async_callback_url,
                 channel_id, order, payee_account_id, payer_account_id):
    payment_id = oid.direct_pay_id(payer_account_id)
    created_on = datetime.now()

    create_payment(payment_id, channel_id, payer_account_id, payee_account_id, order, amount,
                   client_callback_url, client_async_callback_url, created_on)

    return payment_id