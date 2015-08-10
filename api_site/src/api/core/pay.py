# -*- coding: utf-8 -*-
from ._dba import create_payment
from .ipay import transaction
from .util.attr_dict import AttrDict


class PaymentCreationFailedError(Exception):
    def __init__(self):
        message = "Cannot create pay record."
        super(PaymentCreationFailedError, self).__init__(message)



def pay(trade_id, payer_account_id, payer_created_on, payee_account_id, request_from_ip, product_name, product_desc,
        traded_on, amount):
    payment_id = create_payment(trade_id, product_desc, payer_account_id, payee_account_id, amount)
    if not payment_id:
        raise PaymentCreationFailedError()

    payer = AttrDict(id=payer_account_id, created_on=payer_created_on)
    return transaction.pay(
        payer=payer,
        ip=request_from_ip,
        order_no=payment_id,
        order_name=product_name,
        order_desc=product_desc,
        ordered_on=traded_on,
        amount=amount
    )
