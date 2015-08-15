# -*- coding: utf-8 -*-
from datetime import datetime

from ._dba import find_payment_by_order_no, create_payment, find_payment_by_id, update_payment_state, PAYMENT_STATE
from .util import oid
from api.account import find_or_create_account, find_user_domain_id_by_channel, get_account_by_id, \
    get_secured_account_id
from api import config
from api.core import generate_pay_order, pay as core_pay
from api.util import req
from api.util.uuid import encode_uuid
from pytoolbox.util.dbs import transactional


class Order(object):
    def __init__(self, no, name, desc, created_on):
        self.no = no
        self.name = name
        self.desc = desc
        self.created_on = created_on
        self.category = u'虚拟商品'


class PaymentNotFoundError(IOError):
    def __init__(self, payment_id):
        message = "Payment[secured_payment_id={0}] doesn't exist.".format(payment_id)
        super(PaymentNotFoundError, self).__init__(message)


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
    if not pay_record:
        raise PaymentNotFoundError(payment_id)

    pay_form = _pay_with_core(pay_record)
    if not pay_form:
        raise CorePayError(payment_id)

    return pay_form


def _pay_with_core(pay_record):
    payer_account_id = pay_record['payer_account_id']
    secured_account_id = get_secured_account_id()
    amount = pay_record['amount']

    order_id = generate_pay_order(pay_record['id'], payer_account_id, secured_account_id, amount, u'未支付',
                                  pay_record['product_desc'])

    pay_form = core_pay(
        order_id=order_id,
        payer_account_id=payer_account_id,
        payee_account_id=secured_account_id,
        request_from_ip=req.ip(),
        product_name=pay_record['product_name'],
        product_desc=pay_record['product_desc'],
        traded_on=pay_record['ordered_on'],
        amount=amount
    )
    return pay_form


def update_payment_to_be_success(pay_record_id):
    update_payment_state(pay_record_id, PAYMENT_STATE.SUCCESS)


def get_sync_callback_url_of_payment(pay_record_id):
    pay_record = find_payment_by_id(pay_record_id)
    return pay_record['client_callback_url']


def generate_pay_url(_id):
    return _generate_notification_url(config.ZiYouTong.CallbackInterface.PAY_URL, _id)


def _generate_notification_url(relative_url, id, **kwargs):
    params = {'uuid': encode_uuid(id)}
    params.update(kwargs)
    relative_url = relative_url.format(**params)
    return config.Host.API_GATEWAY + relative_url


def _new_payment(amount, client_callback_url, client_async_callback_url,
                 channel_id, order, payee_account_id, payer_account_id):
    payment_id = oid.direct_pay_id(payer_account_id)
    created_on = datetime.now()

    create_payment(payment_id, channel_id, payer_account_id, payee_account_id, order, amount,
                   client_callback_url, client_async_callback_url, created_on)

    return payment_id