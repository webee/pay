# -*- coding: utf-8 -*-
from lianlian_api import parse_request_data as _parse_request_data, request as _request
from lianlian_api import sign_params, md5_sign_params, rsa_sign_params
from .bankcard import query_bin as _query_bin
from .pay import pay as _pay
from .pay_to_bankcard import pay_to_bankcard as _pay_to_bankcard
from .query_order import query_order as _query_order
from .refund import refund as _refund
from .lianlian_config import config
from .util import generate_notification_url as _generate_notification_url
from api.util.uuid import encode_uuid, decode_uuid


def parse_request_data(raw_data):
    return _parse_request_data(raw_data)


def request(api_url, params):
    return _request(api_url, params)


def pay(payer_account_id, order_no, ordered_on, order_name, order_desc, amount, notification_url):
    return _pay(payer_account_id, order_no, ordered_on, order_name, order_desc, amount, notification_url)


def query_bankcard_bin(card_no):
    return _query_bin(card_no)


def pay_to_bankcard(no_order, money_order, info_order, notify_url, bankcard):
    return _pay_to_bankcard(no_order, money_order, info_order, notify_url, bankcard)


def refund(refund_id, refunded_on, amount, paybill_id, url_root):
    return _refund(refund_id, refunded_on, amount, paybill_id, url_root)


def query_order():
    return _query_order()


def is_sending_to_me(partner_id):
    return partner_id == config.oid_partner


def is_valid_transaction(oid_partner, transaction_id, uuid):
    return is_sending_to_me(oid_partner) and transaction_id == decode_uuid(uuid)


def generate_pay_notification_url(id):
    return _generate_notification_url(config.payment.notify_url, id)
