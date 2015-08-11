# -*- coding: utf-8 -*-
from api.core import refund as core_refund
from ._dba import create_refund
from api.secured_transaction.payment.postpay import mark_payment_as_refunding, mark_payment_as_refunded, \
    mark_payment_as_refund_failed


def apply_to_refund(pay_record, amount, async_callback_url):
    payment_id = pay_record.id
    refund_payee_account_id = pay_record.payer_account_id
    refund_payer_account_id = pay_record.payee_account_id

    refund_id = create_refund(
        payment_id=payment_id,
        payer_account_id=refund_payer_account_id,
        payee_account_id=refund_payee_account_id,
        amount=amount,
        async_callback_url=async_callback_url
    )
    trade_info = '活动退款：%s' % pay_record['product_name']
    core_refund(payment_id, amount, trade_info)

    mark_payment_as_refunding(payment_id)

    return refund_id


def after_refunded(payment_id, is_successful_refund):
    if is_successful_refund:
        mark_payment_as_refunded(payment_id)
    else:
        mark_payment_as_refund_failed(payment_id)
