# -*- coding: utf-8 -*-
from ._dba import create_charged_withdraw, update_withdraw_state, CHARGED_WITHDRAW_STATE
from api.account import get_secured_account_id
from api.core import apply_to_withdraw, transfer


def charged_withdraw(account_id, bankcard_id, amount, charged_fee, callback_url):
    actual_withdraw_amount = amount - charged_fee
    charged_withdraw_id = create_charged_withdraw(account_id, bankcard_id, actual_withdraw_amount, charged_fee,
                                                  callback_url)

    if apply_to_withdraw(account_id, bankcard_id, actual_withdraw_amount, callback_url):
        _charge_fee(charged_withdraw_id, account_id, charged_fee)

    return charged_withdraw_id


def _charge_fee(charged_withdraw_id, account_id, fee):
    secured_account_id = get_secured_account_id()
    transfer(charged_withdraw_id, u'提现手续费', account_id, secured_account_id, fee)
    update_withdraw_state(charged_withdraw_id, CHARGED_WITHDRAW_STATE.CHARGED_FEE)
