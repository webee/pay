# coding=utf-8
from . import dba
from old_api.commons.notify import notify_client
from old_api.constant import RefundState


def try_notify_client(refund_id):
    from old_api.task import pay_tasks

    refund_order = dba.get_refund(refund_id)
    url = refund_order.callback_url
    payment = dba.get_payment_by_id(refund_order.payment_id)

    if refund_order.state == RefundState.SUCCESS:
        params = {'code': 0, 'client_id': payment.client_id, 'order_id': payment.order_id,
                  'amount': refund_order.amount}
    elif refund_order.state == RefundState.FAILED:
        params = {'code': 1, 'client_id': payment.client_id, 'order_id': payment.order_id,
                  'amount': refund_order.amount}

    if not notify_client(url, params):
        # other notify process.
        pay_tasks.refund_notify.delay(url, params)