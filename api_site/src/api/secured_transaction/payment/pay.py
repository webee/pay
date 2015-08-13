# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ._dba import find_payment_by_id
from api.core import pay as core_pay, generate_pay_order
from api.account import get_account_by_id, get_secured_account_id
from api.util import req


class PaymentNotFoundError(IOError):
    def __init__(self, payment_id):
        message = "Payment[secured_payment_id={0}] doesn't exist.".format(payment_id)
        super(PaymentNotFoundError, self).__init__(message)


class CorePayError(Exception):
    def __init__(self, payment_id):
        message = "Cannot pay[secured_payment_id={0}] to guaranteed account.".format(payment_id)
        super(CorePayError, self).__init__(message)


def pay_by_id(payment_id):
    pay_record = find_payment_by_id(payment_id)
    if pay_record is None:
        raise PaymentNotFoundError(payment_id)

    pay_form = _pay_with_core(pay_record)
    if not pay_form:
        raise CorePayError(payment_id)

    return pay_form


def _pay_with_core(pay_record):
    payer_account_id = pay_record['payer_account_id']
    payee_account_id = pay_record['payee_account_id']
    amount = pay_record['amount']
    desc = pay_record['product_desc']

    order_id = generate_pay_order(pay_record['id'], payer_account_id, payee_account_id, amount, u'未支付', desc)

    secured_account_id = get_secured_account_id()
    payer = get_account_by_id(payer_account_id)
    pay_form = core_pay(
        order_id=order_id,
        payer_account_id=payer_account_id,
        payee_account_id=secured_account_id,
        request_from_ip=req.ip(),
        product_name=pay_record['product_name'],
        product_desc=u'担保支付申请：%s' % pay_record['product_name'],
        traded_on=pay_record['ordered_on'],
        amount=amount
    )
    return pay_form
