# -*- coding: utf-8 -*-
from __future__ import unicode_literals
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
    payment = _find_payment(payment_id)
    if payment is None:
        raise PaymentNotFoundError(payment_uuid)

    payer_id = payment['payer_account_id']
    payer = _find_account(payer_id)

    return transaction.pay(
        payer=payer,
        ip=req.ip(),
        order_no=payment_id,
        order_name=payment['product_name'],
        order_desc=payment['product_desc'],
        ordered_on=payment['ordered_on'],
        amount=payment['amount'],
        return_url=generate_pay_return_url(payment_id),
        notification_url=payment['callback_url']
    )


def _find_account(id):
    return from_db().get('SELECT * FROM account WHERE id=%(id)s', id=id)


def _find_payment(payment_id):
    return from_db().get(
        """
            SELECT payer_account_id, order_id, product_name, product_desc, amount, ordered_on, callback_url
              FROM payment
              WHERE id = %(id)s
        """,
        id=payment_id)
