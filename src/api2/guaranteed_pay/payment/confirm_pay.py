# -*- coding: utf-8 -*-
from ._dba import confirm_to_pay
from api2 import core
from api2.account import get_secured_account_id
from pytoolbox.util.dbe import transactional


@transactional
def confirm_payment(pay_record):
    payment_id = pay_record['id']
    secured_account_id = get_secured_account_id()
    payee_account_id = pay_record['payee_account_id']
    amount = pay_record['amount']

    confirm_to_pay_request_id = confirm_to_pay(payment_id, payee_account_id, amount)
    core.transfer(confirm_to_pay_request_id, secured_account_id, payee_account_id, amount)
