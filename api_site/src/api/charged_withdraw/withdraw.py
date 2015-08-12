# -*- coding: utf-8 -*-
from ._dba import create_charged_withdraw, update_withdraw_state, CHARGED_WITHDRAW_STATE, find_charged_withdraw_by_id
from api.account import get_secured_account_id
from api.core import apply_to_withdraw, transfer


def charged_withdraw(account_id, bankcard_id, amount, charged_fee, callback_url):
    actual_withdraw_amount = amount - charged_fee
    charged_withdraw_id = create_charged_withdraw(account_id, bankcard_id, actual_withdraw_amount, charged_fee,
                                                  callback_url)

    if apply_to_withdraw(charged_withdraw_id, account_id, bankcard_id, actual_withdraw_amount, ''):
        _charge_fee(charged_withdraw_id, account_id, charged_fee)

    return charged_withdraw_id


def succeed_withdraw(charged_withdraw_id):
    update_withdraw_state(charged_withdraw_id, CHARGED_WITHDRAW_STATE.SUCCESS)


def fail_withdraw(charged_withdraw_id):
    charged_withdraw_record = find_charged_withdraw_by_id(charged_withdraw_id)
    to_account_id = charged_withdraw_record['account_id']
    fee = charged_withdraw_id['fee']
    secured_account_id = get_secured_account_id()

    transfer(charged_withdraw_id, u'提现失败，手续费退回', secured_account_id, to_account_id, fee)


def _charge_fee(charged_withdraw_id, account_id, fee):
    secured_account_id = get_secured_account_id()
    transfer(charged_withdraw_id, u'提现手续费', account_id, secured_account_id, fee)
    update_withdraw_state(charged_withdraw_id, CHARGED_WITHDRAW_STATE.CHARGED_FEE)
