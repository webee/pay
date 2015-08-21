# coding=utf-8
import os
import requests
from sample_site import config
from decimal import Decimal
from tools.mylog import get_logger


logger = get_logger(__name__)

_uid_accounts = {}


def _generate_api_url(url, **kwargs):
    url = url.lstrip('/')
    url = os.path.join(config.PayAPI.ROOT_URL, url.format(**kwargs))
    logger.info("request url %s" % url)
    return url


def get_account_user_id(user_id):
    if user_id not in _uid_accounts:
        url = _generate_api_url(config.PayAPI.GET_CREATE_ACCOUNT_ID_URL,
                                user_domain_name=config.PayAPI.USER_DOMAIN_NAME, user_id=user_id)
        req = requests.post(url)
        if req.status_code == 200:
            res = req.json()
            _uid_accounts[user_id] = res['account_user_id']
    return _uid_accounts.get(user_id)


def get_user_balance(user_id):
    account_user_id = get_account_user_id(user_id)
    url = _generate_api_url(config.PayAPI.GET_USER_BALANCE_URL, account_user_id=account_user_id)
    req = requests.get(url)

    if req.status_code == 200:
        data = req.json()
        print data
        return data['data']
    return {'total': Decimal(0), 'available': Decimal(0), 'frozen': Decimal(0)}


def request_prepay(params):
    url = _generate_api_url(config.PayAPI.PRE_PAY_URL)
    req = requests.post(url, params)
    return req.json()


def request_refund(params):
    url = _generate_api_url(config.PayAPI.REFUND_URL)
    return requests.post(url, params)


def request_withdraw(user_id, params):
    account_user_id = get_account_user_id(user_id)
    url = _generate_api_url(config.PayAPI.WITHDRAW_URL, account_user_id=account_user_id)
    return requests.post(url, params)


def request_confirm_guarantee_payment(params):
    url = _generate_api_url(config.PayAPI.CONFIRM_GUARANTEE_PAYMENT_URL)
    req = requests.post(url, params)
    return req.json()
