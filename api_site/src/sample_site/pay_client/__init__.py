# coding=utf-8
import os
import requests
from functools import wraps
from decimal import Decimal
from pytoolbox.util.sign import SignType, Signer
from pytoolbox.util import pmc_config
from pytoolbox.util.log import get_logger
from .config import Config


logger = get_logger(__name__)


class PayClient(object):

    def __init__(self):
        self.config = Config()
        self.signer = Signer('key', 'sign')
        self._uid_accounts = {}

    def init_config(self, env_config):
        pmc_config.merge_config(self.config, env_config)
        self.signer.init(self.config.MD5_KEY, self.config.CHANNEL_PRI_KEY, self.config.LVYE_PUB_KEY)

    def verify(self, data, do_not_check=True):
        if do_not_check:
            return True
        sing_type = data.get('sign_type')
        channel_name = data.get('channel_name')
        if channel_name != self.config.CHANNEL_NAME:
            return False

        return self.signer.verify(data, sing_type)

    def verify_request(self, f):
        from flask import request

        @wraps(f)
        def wrapper(*args, **kwargs):
            is_verify_pass = True
            try:
                data = request.values
                # check perm
                channel_name = data.get('channel_name')
                if channel_name != self.config.CHANNEL_NAME:
                    is_verify_pass = False

                # verify sign
                sign_type = data['sign_type']
                is_verify_pass = self.signer.verify(data, sign_type)
            except Exception as e:
                logger.exception(e)
                is_verify_pass = False

            request.__dict__['is_verify_pass'] = is_verify_pass
            return f(*args, **kwargs)
        return wrapper

    def request(self, url, params, sign_type=SignType.RSA, method='post'):
        params['sign_type'] = sign_type
        params['channel_name'] = self.config.CHANNEL_NAME
        params['sign'] = self.signer.sign(params, sign_type)

        req = requests.request(method, url, data=params)
        if req.status_code == 200:
            data = req.json()
            if self.verify(data):
                return data
        logger.warn('bad request: {0}, {1}'.format(req.status_code, req.text))
        return None

    def _generate_api_url(self, url, **kwargs):
        url = url.lstrip('/')
        url = os.path.join(self.config.ROOT_URL, url.format(**kwargs))
        logger.info("request url %s" % url)
        return url

    def get_account_user_id(self, user_id):
        if user_id not in self._uid_accounts:
            url = self._generate_api_url(self.config.GET_CREATE_ACCOUNT_ID_URL,
                                         user_domain_name=self.config.USER_DOMAIN_NAME, user_id=user_id)
            req = requests.post(url)
            if req.status_code == 200:
                res = req.json()
                self._uid_accounts[user_id] = res['account_user_id']
        return self._uid_accounts.get(user_id)

    def get_user_balance(self, user_id):
        account_user_id = self.get_account_user_id(user_id)
        url = self._generate_api_url(self.config.GET_USER_BALANCE_URL, account_user_id=account_user_id)
        req = requests.get(url)

        if req.status_code == 200:
            data = req.json()
            print data
            return data['data']
        return {'total': Decimal(0), 'available': Decimal(0), 'frozen': Decimal(0)}

    def prepay(self, params):
        url = self._generate_api_url(self.config.PREPAY_URL)
        return self.request(url, params)

    def refund(self, params):
        url = self._generate_api_url(self.config.REFUND_URL)
        return requests.post(url, params)

    def withdraw(self, user_id, params):
        account_user_id = self.get_account_user_id(user_id)
        url = self._generate_api_url(self.config.WITHDRAW_URL, account_user_id=account_user_id)
        return requests.post(url, params)

    def confirm_guarantee_payment(self, params):
        url = self._generate_api_url(self.config.CONFIRM_GUARANTEE_PAYMENT_URL)
        req = requests.post(url, params)
        return req.json()

    def list_user_bankcards(self, user_id):
        account_user_id = self.get_account_user_id(user_id)
        url = self._generate_api_url(self.config.LIST_USER_BANKCARDS_URL, account_user_id=account_user_id)
        req = requests.get(url)

        if req.status_code == 200:
            return req.json()['bankcards']
        return []
