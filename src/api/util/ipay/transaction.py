# -*- coding: utf-8 -*-

from lianlian_api import parse_request_data

from .bankcard import query_bin as _query_bin
from .pay import pay as _pay
from .pay_to_bankcard import pay_to_bankcard as _pay_to_bankcard


def pay(payer_account_id, order_no, ordered_on, order_name, order_desc, amount, notification_url):
    return _pay(payer_account_id, order_no, ordered_on, order_name, order_desc, amount, notification_url)


def query_bankcard_bin(card_no):
    return _query_bin(card_no)


def pay_to_bankcard(no_order, money_order, info_order, notify_url, bankcard):
    return _pay_to_bankcard(no_order, money_order, info_order, notify_url, bankcard)
