# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from ._dba import confirm_to_pay, update_payment_state, PAYMENT_STATE
from api.core import transfer as core_transfer, update_order_state
from api.account import get_secured_account_id
from pytoolbox.util.dbe import transactional


@transactional
def confirm_payment(pay_record):
    payment_id = pay_record['id']
    secured_account_id = get_secured_account_id()
    payee_account_id = pay_record['payee_account_id']
    amount = pay_record['amount']

    confirm_to_pay_request_id = confirm_to_pay(payment_id, payee_account_id, amount)
    trade_info = u'担保支付确认：[{0}] {1}'.format(pay_record['order_id'], pay_record['product_name'])
    core_transfer(confirm_to_pay_request_id, trade_info, secured_account_id, payee_account_id, amount)

    update_payment_state(payment_id, PAYMENT_STATE.CONFIRMED)

    update_order_state(payment_id, u'已到账')

    return payment_id
