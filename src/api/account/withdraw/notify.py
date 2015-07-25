# coding=utf-8
from api.account.withdraw import dba
from api.constant import WithdrawState


def try_notify_client(withdraw_id):
    from api.task import pay_tasks

    withdraw_order = dba.get_withdraw(withdraw_id)
    url = withdraw_order.callback_url

    if withdraw_order.state == WithdrawState.SUCCESS:
        params = {'code': 0, 'account_id': withdraw_order['account_id'], 'order_id': withdraw_id}
    elif withdraw_order.state == WithdrawState.FAILED:
        params = {'code': 1, 'msg': 'failed', 'account_id': withdraw_order['account_id'], 'order_id': withdraw_id}

    if not notify_client(url, params):
        # other notify process.
        pay_tasks.withdraw_notify.delay(url, params)


def notify_client(url, params):
    import requests

    req = requests.post(url, params)
    if req.status_code == 200:
        data = req.json()
        if data['code'] == 0:
            return True
