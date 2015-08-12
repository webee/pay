# -*- coding: utf-8 -*-
from api.core import refund as core_refund
from ._dba import create_refund, find_refunded_payment_by_refund_id
from api.secured_transaction.payment.postpay import mark_payment_as_refunding, mark_payment_as_refunded, \
    mark_payment_as_refund_failed
from api.util.notify import notify_client


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
    trade_info = u'活动退款：%s' % pay_record['product_name']
    core_refund(payment_id, amount, trade_info)

    mark_payment_as_refunding(payment_id)

    return refund_id


def after_refunded(payment_id, refund_id, is_successful_refund):
    if is_successful_refund:
        mark_payment_as_refunded(payment_id)
    else:
        mark_payment_as_refund_failed(payment_id)

    _try_notify_client(refund_id, is_successful_refund)


def _try_notify_client(refund_id, is_successful_refund):
    refunded_payment = find_refunded_payment_by_refund_id(refund_id)
    url = refunded_payment.refund_callback_url

    if is_successful_refund:
        params = {'code': 0, 'client_id': refunded_payment.client_id, 'order_id': refunded_payment.order_id,
                  'amount': refunded_payment.refund_amount}
    else:
        params = {'code': 1, 'client_id': refunded_payment.client_id, 'order_id': refunded_payment.order_id,
                  'amount': refunded_payment.refund_amount}

    if not notify_client(url, params):
        # other notify process.
        from api.task import tasks
        tasks.refund_notify.delay(url, params)
