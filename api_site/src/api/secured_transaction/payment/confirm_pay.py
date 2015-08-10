# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from ._dba import confirm_to_pay, update_payment_state, PAYMENT_STATE
from api import core
from api.account import get_secured_account_id
from pytoolbox.util.dbe import transactional


@transactional
def confirm_payment(pay_record):
    payment_id = pay_record['id']
    secured_account_id = get_secured_account_id()
    payee_account_id = pay_record['payee_account_id']
    amount = pay_record['amount']

    confirm_to_pay_request_id = confirm_to_pay(payment_id, payee_account_id, amount)
    trade_info = '担保付款'
    core.transfer(confirm_to_pay_request_id, trade_info, secured_account_id, payee_account_id, amount)

    update_payment_state(payment_id, PAYMENT_STATE.CONFIRMED)

    return payment_id
