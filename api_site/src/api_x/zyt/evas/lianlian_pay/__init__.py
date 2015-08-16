# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import wraps
from flask import url_for, Response
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
from api_x.config import lianlian_pay


NAME = 'LIANLIAN_PAY'


def pay(source, user_id, user_created_on, ip, order_no, order_name, order_desc, amount):
    return_url = lianlian_pay.ROOT_URL + url_for('lianlian_pay_entry.pay_result', pay_source=source)
    notify_url = lianlian_pay.ROOT_URL + url_for('lianlian_pay_entry.pay_notify', pay_source=source)

    return Response(_pay(user_id, user_created_on, ip, order_no, order_name, order_desc, amount,
                         return_url, notify_url))


def refund():
    pass


def pay_to_bankcard():
    pass


def query_bin():
    pass


def is_sending_to_me(partner_id):
    return partner_id == lianlian_pay.OID_PARTNER
