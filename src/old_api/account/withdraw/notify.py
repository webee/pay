# coding=utf-8
from old_api.account.withdraw import dba
from old_api.commons.notify import notify_client
from old_api.constant import WithdrawState


def try_notify_client(withdraw_id):
    from old_api.task import pay_tasks

    withdraw_order = dba.get_withdraw(withdraw_id)
    url = withdraw_order.callback_url
    amount = withdraw_order.amount
    account_id = withdraw_order.account_id

    if withdraw_order.state == WithdrawState.SUCCESS:
        params = {'code': 0, 'account_id': account_id, 'order_id': withdraw_id, 'amount': amount}
    elif withdraw_order.state == WithdrawState.FAILED:
        params = {'code': 1, 'msg': 'failed', 'account_id': account_id, 'order_id': withdraw_id, 'amount': amount}

    if not notify_client(url, params):
        # other notify process.
        pay_tasks.withdraw_notify.delay(url, params)
