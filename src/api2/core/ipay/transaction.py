# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from functools import wraps
from flask import request
from urlparse import urljoin

from .error import *
from .lianlian.api import parse_and_verify_request_data
from .lianlian.bankcard import query_bin as _query_bin
from .lianlian.notification import Notification
from .lianlian.pay import pay as _pay
from .lianlian.pay_to_bankcard import pay_to_bankcard as _pay_to_bankcard
from .lianlian.query_order import query_order as _query_order
from .lianlian.refund import refund as _refund
from .lianlian.validation import is_sending_to_me as _is_sending_to_me
from . import zyt_url
from api.util.uuid import decode_uuid
from api2.util.uuid import encode_uuid
from pytoolbox import config as _config


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
    notify_url = generate_refund_notification_url(refund_id)
    return _refund(refund_id, refunded_on, amount, paybill_id, notify_url)


def query_withdraw_order(withdraw_id):
    return _query_order(withdraw_id)


def is_valid_transaction(oid_partner, transaction_id, uuid):
    return _is_sending_to_me(oid_partner) and transaction_id == decode_uuid(uuid)


def generate_pay_url(id):
    return _generate_notification_url(zyt_url.pay, id)


def generate_pay_return_url(id):
    return _generate_notification_url(zyt_url.pay_return, id)


def generate_pay_notification_url(id):
    return _generate_notification_url(zyt_url.pay_notify, id)


def generate_withdraw_notification_url(account_id, id):
    return _generate_notification_url(zyt_url.pay_to_bankcard_notify, id, account_id=account_id)


def generate_refund_notification_url(id):
    return _generate_notification_url(zyt_url.refund_notify, id)


def _generate_notification_url(relative_url, id, **kwargs):
    params = {'uuid': encode_uuid(id)}
    params.update(kwargs)
    relative_url = relative_url.format(**params)
    root_url = _config.get('hosts', 'api_gateway')
    return urljoin(root_url, relative_url)
