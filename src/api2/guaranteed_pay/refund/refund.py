# -*- coding: utf-8 -*-
from api2 import core
from ._dba import create_refund


def apply_to_refund(pay_record, amount, async_callback_url):
    payment_id = pay_record.id
    payer_account_id = pay_record.payer_account_id
    payee_account_id = pay_record.payee_account_id

    refund_id = create_refund(
        payment_id=payment_id,
        payer_account_id=payer_account_id,
        payee_account_id=payee_account_id,
        amount=amount,
        async_callback_url=async_callback_url
    )
    core.refund(payment_id, amount)

    return refund_id
