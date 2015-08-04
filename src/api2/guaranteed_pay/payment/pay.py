# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .dba import find_payment_by_id
from api2 import core
from api2.account import get_account_by_id
from .secured_account import get_secured_account_id
from api.util import req


class PaymentNotFoundError(Exception):
    def __init__(self, payment_id):
        message = "payment: {0} not exists.".format(payment_id)
        super(PaymentNotFoundError, self).__init__(message)


def pay_by_uuid(payment_id):
    pay_record = find_payment_by_id(payment_id)
    if pay_record is None:
        raise PaymentNotFoundError(payment_id)

    payer_id = pay_record['payer_account_id']
    payer = get_account_by_id(payer_id)
    secured_account_id = get_secured_account_id(payer['client_id'])
    return core.pay(
        trade_id=payment_id,
        payer_account_id=payer_id,
        payer_created_on=payer['created_on'],
        payee_account_id=secured_account_id,
        request_from_ip=req.ip(),
        product_name=pay_record['product_name'],
        product_desc=pay_record['product_desc'],
        traded_on=pay_record['ordered_on'],
        amount=pay_record['amount']
    )
