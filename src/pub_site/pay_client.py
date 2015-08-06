# coding=utf-8
import os
import requests
from pub_site import config


_accounts = {}


def _generate_api_url(url, **kwargs):
    return os.path.join(config.PayAPI.ROOT_URL, url.format(**kwargs))


def get_account_id(uid):
    if uid not in _accounts:
        url = _generate_api_url(config.PayAPI.GET_ACCOUNT_INFO_URL, user_domain_id=config.USER_DOMAIN_ID, uid=uid)
        req = requests.get(url)
        if req.status_code == 200:
            res = req.json()
            _accounts[uid] = res['account_id']
    return _accounts.get(uid)


def get_user_balance(uid):
    account_id = get_account_id(uid)
    url = _generate_api_url(config.PayAPI.GET_USER_BALANCE_URL, account_id=account_id)
    req = requests.get(url)

    if req.status_code == 200:
        data = req.json()
        return data['balance']


def get_user_cash_records(uid):
    account_id = get_account_id(uid)
    url = _generate_api_url(config.PayAPI.GET_USER_CASH_RECORDS_URL, account_id=account_id)

    req = requests.get(url)

    if req.status_code == 200:
        return req.json()
    return []
