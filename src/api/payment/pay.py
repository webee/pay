# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .dba import find_payment_by_id
from api.util.ipay import transaction
from api.util.ipay.transaction import generate_pay_return_url
from api.util.uuid import decode_uuid
from tools.dbe import from_db
from api.util import req


class PaymentNotFoundError(Exception):
    def __init__(self, payment_uuid):
        message = "payment: {0} not exists.".format(payment_uuid)
        super(PaymentNotFoundError, self).__init__(message)


def pay_by_uuid(payment_uuid):
    payment_id = decode_uuid(payment_uuid)
    pay_record = find_payment_by_id(payment_id)
    if pay_record is None:
        raise PaymentNotFoundError(payment_uuid)

    payer_id = pay_record['payer_account_id']
    payer = _find_account(payer_id)

    return transaction.pay(
        payer=payer,
        ip=req.ip(),
        order_no=payment_id,
        order_name=pay_record['product_name'],
        order_desc=pay_record['product_desc'],
        ordered_on=pay_record['ordered_on'],
        amount=pay_record['amount'],
        return_url=generate_pay_return_url(payment_id),
        notification_url=pay_record['callback_url']
    )


def _find_account(id):
    return from_db().get('SELECT * FROM account WHERE id=%(id)s', id=id)

