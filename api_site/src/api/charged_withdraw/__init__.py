# -*- coding: utf-8 -*-

def apply_to_charged_withdraw(account_id, bankcard_id, amount, charged_fee, callback_url=''):
    from .withdraw import charged_withdraw
    return charged_withdraw(account_id, bankcard_id, amount, charged_fee, callback_url)
