# coding=utf-8
from . import dba
from api.commons.notify import notify_client
from api.constant import RefundState


def try_notify_client(refund_id):
    from api.task import pay_tasks

    refund_order = dba.get_refund(refund_id)
    url = refund_order.callback_url

    if refund_order.state == RefundState.SUCCESS:
        params = {'code': 0,
                  'payer_account_id': refund_order['payer_account_id'],
                  'payee_account_id': refund_order['payee_account_id'],
                  'order_id': refund_id}
    elif refund_order.state == RefundState.FAILED:
        params = {'code': 1, 'msg': 'failed',
                  'payer_account_id': refund_order['payer_account_id'],
                  'payee_account_id': refund_order['payee_account_id'],
                  'order_id': refund_id}

    if not notify_client(url, params):
        # other notify process.
        pay_tasks.refund_notify.delay(url, params)
