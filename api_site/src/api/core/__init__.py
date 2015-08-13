# -*- coding: utf-8 -*-

class ZytCoreError(Exception):
    def __init__(self, message):
        super(ZytCoreError, self).__init__(message)


class ConditionalError(ZytCoreError):
    def __init__(self, message):
        super(ConditionalError, self).__init__(message)



def pay(order_id, payer_account_id, payer_created_on, payee_account_id, request_from_ip, product_name, product_desc,
        traded_on, amount):
    from .pay import pay as _pay
    return _pay(order_id, payer_account_id, payer_created_on, payee_account_id, request_from_ip, product_name,
                product_desc, traded_on, amount)


def transfer(order_id, trade_info, payer_account_id, payee_account_id, amount):
    from .transfer import transfer as _transfer
    return _transfer(order_id, trade_info, payer_account_id, payee_account_id, amount)


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


def get_bankcard_by_id(bankcard_id):
    from .bankcard import get_bankcard_by_id as _get_bankcard_by_id
    return _get_bankcard_by_id(bankcard_id)


def apply_to_withdraw(order_id, account_id, bankcard_id, amount, callback_url):
    from .withdraw import apply_to_withdraw as _apply_to_withdraw
    return _apply_to_withdraw(order_id, account_id, bankcard_id, amount, callback_url)


def list_unfailed_withdraw(account_id):
    from .withdraw import list_unfailed_withdraw as _list_unfailed_withdraw
    return _list_unfailed_withdraw(account_id)


def get_withdraw_basic_info_by_id(withdraw_id):
    from .withdraw import get_withdraw_basic_info_by_id as _get_withdraw_basic_info_by_id
    return _get_withdraw_basic_info_by_id(withdraw_id)


def refund(order_id, payment_order_source_id, amount, trade_info):
    from .refund import refund as _refund
    return _refund(order_id, payment_order_source_id, amount, trade_info)


def get_cash_balance(account_id):
    from .balance import get_cash_balance as _get_cash_balance
    return _get_cash_balance(account_id)


def list_cash_transaction_logs(account_id, q, side, tp, page_no, page_size):
    from api.core import transaction_log
    return transaction_log.get_user_cash_account_records(account_id, q, side, tp, page_no, page_size)


def generate_pay_order(source_id, from_account_id, to_account_id, amount, state, info):
    from .order import generate_pay_order as _generate_pay_order
    return _generate_pay_order(source_id, from_account_id, to_account_id, amount, state, info)


def generate_refund_order(source_id, from_account_id, to_account_id, amount, state, info):
    from .order import generate_refund_order as _generate_refund_order
    return _generate_refund_order(source_id, from_account_id, to_account_id, amount, state, info)


def generate_transfer_order(source_id, from_account_id, to_account_id, amount, state, info):
    from .order import generate_transfer_order as _generate_transfer_order
    return _generate_transfer_order(source_id, from_account_id, to_account_id, amount, state, info)


def generate_withdraw_order(source_id, account_id, amount, state, info):
    from .order import generate_withdraw_order as _generate_withdraw_order
    return _generate_withdraw_order(source_id, account_id, amount, state, info)


def update_order_state(source_id, state):
    from .order import update_order_state as _update_order_state
    return _update_order_state(source_id, state)