# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ._dba import find_payment_by_id, PAYMENT_STATE, update_payment_state, secure_payment
from api2 import core
from api2.account import get_account_by_id, get_secured_account_id
from pytoolbox.util.dbe import transactional
from api.util import req


class PaymentNotFoundError(Exception):
    def __init__(self, payment_id):
        message = "Payment[guaranteed_payment.id={0}] doesn't exist.".format(payment_id)
        super(PaymentNotFoundError, self).__init__(message)


class CorePayError(Exception):
    def __init__(self, payment_id):
        message = "Cannot pay[guaranteed_payment.id={0}] to guaranteed account.".format(payment_id)
        super(CorePayError, self).__init__(message)


def pay_by_id(payment_id):
    pay_record = find_payment_by_id(payment_id)
    if pay_record is None:
        raise PaymentNotFoundError(payment_id)

    payer_account_id = pay_record['payer_account_id']
    payer = get_account_by_id(payer_account_id)
    secured_account_id = get_secured_account_id()
    amount = pay_record['amount']
    pay_form = core.pay(
        trade_id=payment_id,
        payer_account_id=payer_account_id,
        payer_created_on=payer['created_on'],
        payee_account_id=secured_account_id,
        request_from_ip=req.ip(),
        product_name=pay_record['product_name'],
        product_desc=pay_record['product_desc'],
        traded_on=pay_record['ordered_on'],
        amount=amount
    )
    if not pay_form:
        raise CorePayError(payment_id)

    _put_pay_to_be_secured(payment_id, payer_account_id, amount)

    return pay_form


@transactional
def _put_pay_to_be_secured(payment_id, payer_account_id, amount):
    secure_payment(payment_id, payer_account_id, amount)
    update_payment_state(payment_id, PAYMENT_STATE.SECURED)
