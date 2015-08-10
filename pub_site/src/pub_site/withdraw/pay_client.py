from pub_site import config
from flask.ext.login import current_user
import requests, json, functools

pay_server = config.PayAPI.ROOT_URL
lvye_user_id = config.PayAPI.LVYE_USER_ID


def handle_response(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)
        if 200 <= resp.status_code < 300:
            return {'data': json.loads(resp.content), 'status_code': resp.status_code}
        return {'data': {"message": resp.content}, 'status_code': resp.status_code}

    return _wrapper


class PayClient:
    accounts = {}

    def __init__(self, server=pay_server, user_domain_id=config.USER_DOMAIN_ID):
        self.server = server
        self.user_domain_id = user_domain_id

    @handle_response
    def bind_bankcards(self, card_number, account_name, province_code, city_code, branch_bank_name):
        uid = current_user.user_id
        account_id = self._get_account(uid)['account_id']
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
    def get_bankcards(self):
        uid = current_user.user_id
        account_id = self._get_account(uid)['account_id']
        url = '%s/accounts/%s/bankcards' % (self.server, account_id)
        return requests.get(url)

    @handle_response
    def get_balance(self):
        uid = current_user.user_id
        account_id = self._get_account(uid)['account_id']
        url = '%s/accounts/%s/balance' % (self.server, account_id)
        return requests.get(url)

    @handle_response
    def withdraw(self, amount, bankcard_id, callback_url):
        uid = current_user.user_id
        account_id = self._get_account(uid)['account_id']
        url = '%s/accounts/%s/withdraw' % (self.server, account_id)
        data = {
            'bankcard_id': bankcard_id,
            'amount': amount,
            'callback_url': callback_url
        }
        return requests.post(url, data=data)

    @handle_response
    def transfer_to_lvye(self, amount, order_id, order_info):
        from_id = self._get_account(current_user.user_id)['account_id']
        to_id = self._get_account(lvye_user_id)['account_id']
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
            "client_id": config.PayAPI.CHANNEL_ID,
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

    def _get_account(self, uid):
        if uid in PayClient.accounts:
            return PayClient.accounts[uid]
        url = '%s/user_domains/%s/users/%s/account' % (self.server, self.user_domain_id, uid)
        resp = requests.get(url)
        if resp.status_code != 200:
            return {"account_id": 0}
        account = json.loads(resp.content)
        PayClient.accounts[uid] = account
        return account
