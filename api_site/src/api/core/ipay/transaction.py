# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from functools import wraps
from urlparse import urljoin

from flask import request
from .error import *
from .lianlian.api_access import parse_and_verify_request_data
from .lianlian.bankcard import query_bin as _query_bin
from .lianlian.notification import Notification
from .lianlian.pay import pay as _pay
from .lianlian.pay_to_bankcard import pay_to_bankcard as _pay_to_bankcard, \
    is_successful_withdraw as _is_successful_withdraw, is_failed_withdraw as _is_failed_withdraw
from .lianlian.query_order import query_order as _query_order
from .lianlian.refund import refund as _refund, is_successful_refund as _is_successful_refund
from .lianlian.validation import is_sending_to_me as _is_sending_to_me
from api import config
from api.util.uuid import encode_uuid, decode_uuid

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


def pay(payer, ip, order_no, ordered_on, order_name, order_desc, amount):
    return_url = generate_pay_return_url(order_no)
    notify_url = generate_pay_notification_url(order_no)
    return _pay(payer, ip, order_no, ordered_on, order_name, order_desc, amount, return_url, notify_url)


def query_bankcard_bin(card_no):
    return _query_bin(card_no)


def pay_to_bankcard(withdraw_id, money_order, info_order, bankcard, notify_url):
    return _pay_to_bankcard(withdraw_id, money_order, info_order, bankcard, notify_url)


def refund(refund_id, refunded_on, amount, paybill_id):
    notify_url = generate_refund_notification_url(refund_id)
    return _refund(refund_id, refunded_on, amount, paybill_id, notify_url)


def query_withdraw_order(withdraw_id):
    return _query_order(withdraw_id)


def is_sending_to_me(partner_id):
    return _is_sending_to_me(partner_id)


def is_valid_transaction(oid_partner, transaction_id, uuid):
    return _is_sending_to_me(oid_partner) and transaction_id == decode_uuid(uuid)


def is_successful_withdraw(withdraw_result):
    return _is_successful_withdraw(withdraw_result)


def is_failed_withdraw(withdraw_result):
    return _is_failed_withdraw(withdraw_result)


def is_successful_refund(refund_status):
    return _is_successful_refund(refund_status)


def generate_pay_return_url(id):
    return _generate_notification_url(config.ZiYouTong.CallbackInterface.PAY_URL, id)


def generate_pay_notification_url(id):
    return _generate_notification_url(config.ZiYouTong.CallbackInterface.PAY_NOTIFY_URL, id)


def generate_withdraw_notification_url(account_id, id):
    return _generate_notification_url(config.ZiYouTong.CallbackInterface.PAY_TO_BANKCARD_NOTIFY_URL, id, account_id=account_id)


def generate_refund_notification_url(id):
    return _generate_notification_url(config.ZiYouTong.CallbackInterface.REFUND_NOTIFY_URL, id)


def _generate_notification_url(relative_url, id, **kwargs):
    params = {'uuid': encode_uuid(id)}
    params.update(kwargs)
    relative_url = relative_url.format(**params)
    root_url = config.Host.API_GATEWAY
    return urljoin(root_url, relative_url)
