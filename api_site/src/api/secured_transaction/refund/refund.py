# -*- coding: utf-8 -*-
from ._dba import create_refund, find_refunded_payment_by_refund_id
from api.core import refund as core_refund, generate_refund_order, update_order_state
from api.secured_transaction.payment.postpay import mark_payment_as_refunding, mark_payment_as_refunded, \
    mark_payment_as_refund_failed
from api.util.notify import notify_client
from pytoolbox.util.log import get_logger
import os

_logger = get_logger(__name__, level=os.getenv('LOG_LEVEL', 'INFO'))


def apply_to_refund(pay_record, amount, async_callback_url):
    payment_id = pay_record.id
    from_account_id = pay_record.payee_account_id
    to_account_id = pay_record.payer_account_id

    refund_id = create_refund(
        payment_id=payment_id,
        payer_account_id=from_account_id,
        payee_account_id=to_account_id,
        amount=amount,
        async_callback_url=async_callback_url
    )

    trade_info = u'活动退款：%s' % pay_record['product_name']
    order_id = generate_refund_order(refund_id, from_account_id, to_account_id, amount, u'退款中', trade_info)
    core_refund(order_id, payment_id, amount, trade_info)

    mark_payment_as_refunding(payment_id)

    return refund_id


def after_refunded(payment_id, refund_id, is_successful_refund):
    if is_successful_refund:
        _logger.info('refund succeed with refund id [{0}] and payment_id: [{1}]'.format(refund_id, payment_id))
        _succeed_refund(refund_id, payment_id)
    else:
        _logger.info('refund failed with refund id [{0}] and payment_id: [{1}]'.format(refund_id, payment_id))
        _fail_refund(refund_id, payment_id)

    _try_notify_client(refund_id, is_successful_refund)


def _succeed_refund(refund_id, payment_id):
    mark_payment_as_refunded(payment_id)
    update_order_state(refund_id, u'已完成')


def _fail_refund(refund_id, payment_id):
    mark_payment_as_refund_failed(payment_id)
    update_order_state(refund_id, u'失败')


def _try_notify_client(refund_id, is_successful_refund):
    _logger.info('notify client')
    refunded_payment = find_refunded_payment_by_refund_id(refund_id)
    url = refunded_payment.refund_callback_url
    _logger.info('notify client url: {}'.format(url))
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
