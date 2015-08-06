# -*- coding: utf-8 -*-

class ZytCoreError(Exception):
    def __init__(self, message):
        super(ZytCoreError, self).__init__(message)


class ConditionalError(ZytCoreError):
    def __init__(self, message):
        super(ConditionalError, self).__init__(message)



def pay(trade_id, payer_account_id, payer_created_on, payee_account_id, request_from_ip, product_name, product_desc,
        traded_on, amount):
    from .pay import pay as _pay
    return _pay(trade_id, payer_account_id, payer_created_on, payee_account_id, request_from_ip, product_name,
                product_desc, traded_on, amount)


def transfer(trade_id, payer_account_id, payee_account_id, amount):
    from .transfer import transfer as _transfer
    return _transfer(trade_id, payer_account_id, payee_account_id, amount)


def query_bankcard_bin(card_no):
    from .bankcard import query_bankcard_bin as _query_bankcard_bin
    return _query_bankcard_bin(card_no)


def list_all_bankcards(account_id):
    from .bankcard import list_all_bankcards as _list_all_bankcards
    return _list_all_bankcards(account_id)


def add_bankcard(account_id, card_no, account_name, is_corporate_account, province_code, city_code, branch_bank_name):
    from .bankcard import add_bankcard as _add_bankcard
    return _add_bankcard(account_id, card_no, account_name, is_corporate_account, province_code, city_code,
                         branch_bank_name)


def apply_to_withdraw(account_id, bankcard_id, amount, callback_url):
    from .withdraw import apply_to_withdraw as _apply_to_withdraw
    return _apply_to_withdraw(account_id, bankcard_id, amount, callback_url)


def list_unfailed_withdraw(account_id):
    from .withdraw import list_unfailed_withdraw as _list_unfailed_withdraw
    return _list_unfailed_withdraw(account_id)


def get_withdraw_basic_info_by_id(withdraw_id):
    from .withdraw import get_withdraw_basic_info_by_id as _get_withdraw_basic_info_by_id
    return _get_withdraw_basic_info_by_id(withdraw_id)


def refund(payment_trade_id, amount):
    from .refund import refund as _refund
    return _refund(payment_trade_id, amount)


def get_cash_balance(account_id):
    from .balance import get_cash_balance as _get_cash_balance
    return _get_cash_balance(account_id)