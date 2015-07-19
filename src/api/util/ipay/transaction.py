# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from flask import request

from lianlian_api import parse_and_verify_request_data as _parse_and_verify_request_data
from .bankcard import query_bin as _query_bin
from .notification import Notification
from .pay import pay as _pay
from .pay_to_bankcard import pay_to_bankcard as _pay_to_bankcard
from .query_order import query_order as _query_order
from .refund import refund as _refund
from .lianlian_config import config
from .util import generate_url as _generate_notification_url
from api.util.uuid import decode_uuid


notification = Notification()


def parse_and_verify(notify):
    def parser(**kwargs):
        try:
            verified_data = _parse_and_verify_request_data(request.values, request.data)
            request.__dict__['verified_data'] = verified_data
        except:
            return notification.is_invalid()
        return notify(**kwargs)
    return parser


def pay(payer_account_id, order_no, ordered_on, order_name, order_desc, amount, notification_url):
    return _pay(payer_account_id, order_no, ordered_on, order_name, order_desc, amount, notification_url)


def query_bankcard_bin(card_no):
    return _query_bin(card_no)


def pay_to_bankcard(no_order, money_order, info_order, notify_url, bankcard):
    return _pay_to_bankcard(no_order, money_order, info_order, notify_url, bankcard)


def refund(refund_id, refunded_on, amount, paybill_id):
    return _refund(refund_id, refunded_on, amount, paybill_id)


def query_order():
    return _query_order()


def is_sending_to_me(partner_id):
    return partner_id == config.oid_partner


def is_valid_transaction(oid_partner, transaction_id, uuid):
    return is_sending_to_me(oid_partner) and transaction_id == decode_uuid(uuid)


def generate_pay_url(id):
    return _generate_notification_url(config.payment.redirect_url, id)


def generate_pay_notification_url(id):
    return _generate_notification_url(config.payment.notify_url, id)


def generate_pay_to_bankcard_notification_url(id):
    return _generate_notification_url(config.pay_to_bankcard.notify_url, id)
