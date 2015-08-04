# -*- coding: utf-8 -*-
from ..dba import get_withdraw_by_id, WITHDRAW_STATE
from pytoolbox.util.log import get_logger

_logger = get_logger(__name__)


def try_to_notify_client(withdraw_id):
    from api.task import pay_tasks

    withdraw_order = get_withdraw_by_id(withdraw_id)
    url = withdraw_order['async_callback_url']
    amount = withdraw_order.amount
    account_id = withdraw_order.account_id

    if withdraw_order.state == WITHDRAW_STATE.SUCCESS:
        params = {'code': 0, 'account_id': account_id, 'order_id': withdraw_id, 'amount': amount}
    elif withdraw_order.state == WITHDRAW_STATE.FAILED:
        params = {'code': 1, 'msg': 'failed', 'account_id': account_id, 'order_id': withdraw_id, 'amount': amount}

    if not _notify_client(url, params):
        # other notify process.
        pay_tasks.withdraw_notify.delay(url, params)


def _notify_client(url, params):
    import requests

    try:
        req = requests.post(url, params)
        if req.status_code == 200:
            data = req.json()
            if data['code'] == 0:
                if data['message'] != "OK":
                    # TODO
                    # log it.
                    _logger.warn('notify [{0}, {1}] failed.'.format(url, json.dumps(params)))
                    pass
                return True
    except:
        return False
