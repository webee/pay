from pub_site import config
from flask.ext.login import current_user
import requests
import json
import functools
from pytoolbox.util.log import get_logger
import os
from pub_site import pay_client

logger = get_logger(__name__, level=os.getenv('LOG_LEVEL', 'INFO'))


def handle_response(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)
        if 200 <= resp.status_code < 300:
            return {'data': json.loads(resp.content), 'status_code': resp.status_code}
        return {'data': {"message": resp.content}, 'status_code': resp.status_code}

    return _wrapper


class PayClient:
    account_user_ids = {}

    def __init__(self, server=config.PayAPI.ROOT_URL):
        self.server = server

    @handle_response
    def bind_bankcards(self, card_number, account_name, province_code, city_code, branch_bank_name):
        uid = current_user.user_id
        account_id = pay_client.get_account_user_id(uid)
        url = '%s/accounts/%s/bankcards' % (self.server, account_id)
        data = {
            "card_no": card_number,
            "account_name": account_name,
            "is_corporate_account": 0,
            "province_code": province_code,
            "city_code": city_code,
            "branch_bank_name": branch_bank_name
        }
        return requests.post(url, data=data)

    @handle_response
    def get_balance(self):
        uid = current_user.user_id
        account_id = pay_client.get_account_user_id(uid)
        url = '%s/accounts/%s/balance' % (self.server, account_id)
        return requests.get(url)

    @handle_response
    def withdraw(self, amount, fee, bankcard_id, callback_url=''):
        uid = current_user.user_id
        account_id = pay_client.get_account_user_id(uid)
        url = '%s/accounts/%s/charged-withdraw' % (self.server, account_id)
        data = {
            'bankcard_id': bankcard_id,
            'amount': amount,
            'fee': fee,
            'callback_url': callback_url
        }
        return requests.post(url, data=data)

    @handle_response
    def transfer_to_lvye(self, amount, order_id, order_info):
        from_id = pay_client.get_account_user_id(current_user.user_id)
        to_id = pay_client.get_account_user_id(config.LVYE_USER_NAME)
        url = '%s/accounts/%s/transfer/to/%s' % (self.server, from_id, to_id)
        data = {
            "order_no": order_id,
            "order_info": order_info,
            "amount": amount
        }
        return requests.post(url, data=data)

    @handle_response
    def pay_to_lvye(self, amount, order_id, order_name, order_description, create_on, callback_url):
        url = '%s/direct/pre-pay' % self.server
        data = {
            "channel_name": config.CHANNEL_NAME,
            "payer": current_user.user_id,
            "payee": config.PayAPI.LVYE_USER_ID,
            "order_no": order_id,
            "order_name": order_name,
            "order_desc": order_description,
            "ordered_on": create_on,
            "client_callback_url": callback_url,
            "amount": amount
        }
        return requests.post(url, data=data)
