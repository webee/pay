# -*- coding: utf-8 -*-

from lianlian import withdraw
from lianlian_api import parse_request_data

from .pay import pay as _pay
from .bankcard import query_bin as _query_bin


def pay(payer_account_id, order_no, ordered_on, order_name, order_desc, amount, notification_url):
    return _pay(payer_account_id, order_no, ordered_on, order_name, order_desc, amount, notification_url)


def query_bankcard_bin(card_no):
    return _query_bin(card_no)
