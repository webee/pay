# -*- coding: utf-8 -*-

from lianlian import withdraw, query_bankcard_bin
from lianlian_api import parse_request_data

from .pay import pay as _pay

def pay(payer_account_id, order_no, ordered_on, order_name, order_desc, amount, notification_url):
    return _pay(payer_account_id, order_no, ordered_on, order_name, order_desc, amount, notification_url)
