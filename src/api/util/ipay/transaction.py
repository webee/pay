# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from functools import wraps
from flask import request

from .error import *
from lianlian_api import parse_and_verify_request_data
from .bankcard import query_bin as _query_bin
from .notification import Notification
from .pay import pay as _pay
from .pay_to_bankcard import pay_to_bankcard as _pay_to_bankcard
from .query_order import query_order as _query_order
from .refund import refund as _refund
from .util import generate_url as _generate_notification_url
from .conf import config, zyt_url
from api.util.uuid import decode_uuid


notification = Notification()


def parse_and_verify(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verified_data = parse_and_verify_request_data(request.values, request.data)
            request.__dict__['verified_data'] = verified_data
        except (DictParsingError, InvalidSignError):
            return notification.is_invalid()
        return f(*args, **kwargs)
    return decorated_function


def pay(payer, ip, order_no, ordered_on, order_name, order_desc, amount, return_url, notification_url):
    return _pay(payer, ip, order_no, ordered_on, order_name, order_desc, amount, return_url, notification_url)


def query_bankcard_bin(card_no):
    return _query_bin(card_no)


def pay_to_bankcard(withdraw_id, money_order, info_order, bankcard, notify_url):
    return _pay_to_bankcard(withdraw_id, money_order, info_order, bankcard, notify_url)


def refund(refund_id, refunded_on, amount, paybill_id):
    return _refund(refund_id, refunded_on, amount, paybill_id)


def query_withdraw_order(withdraw_id):
    return _query_order(withdraw_id, dt_order='', oid_paybill='', type_dc=config.order_typedc_pay)


def is_sending_to_me(partner_id):
    return partner_id == config.oid_partner


def is_valid_transaction(oid_partner, transaction_id, uuid):
    return is_sending_to_me(oid_partner) and transaction_id == decode_uuid(uuid)


def generate_pay_url(id):
    return _generate_notification_url(zyt_url.pay, id)


def generate_pay_return_url(id):
    return _generate_notification_url(zyt_url.pay_return, id)


def generate_pay_notification_url(id):
    return _generate_notification_url(zyt_url.pay_notify, id)


def generate_withdraw_notify_url(account_id, id):
    return _generate_notification_url(zyt_url.pay_to_bankcard_notify, id, account_id=account_id)

