# -*- coding: utf-8 -*-
from .pay import pay as _pay
from .transfer import transfer as _transfer
from .bankcard import query_bankcard_bin as _query_bankcard_bin, list_all_bankcards as _list_all_bankcards


def pay(trade_id, payer_account_id, payer_created_on, payee_account_id, request_from_ip, product_name, product_desc,
        traded_on, amount):
    return _pay(trade_id, payer_account_id, payer_created_on, payee_account_id, request_from_ip, product_name,
                product_desc, traded_on, amount)


def transfer(trade_id, payer_account_id, payee_account_id, amount):
    return _transfer(trade_id, payer_account_id, payee_account_id, amount)


def query_bankcard_bin(card_no):
    return _query_bankcard_bin(card_no)


def list_all_bankcards(account_id):
    return _list_all_bankcards(account_id)