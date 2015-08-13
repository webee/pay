# coding=utf-8
import os
import requests
from pub_site import config
from decimal import Decimal
from tools.urls import build_url
from pytoolbox.util.log import get_logger



_uid_accounts = {}
_id_accounts = {}

_logger = get_logger(__name__, level=os.getenv('LOG_LEVEL', 'INFO'))


def _generate_api_url(url, **kwargs):
    url = os.path.join(config.PayAPI.ROOT_URL, url.format(**kwargs))
    _logger.info("request url %s" % url)
    return url


def get_account_id(uid):
    if uid not in _uid_accounts:
        url = _generate_api_url(config.PayAPI.GET_ACCOUNT_ID_URL, user_domain_id=config.USER_DOMAIN_ID, uid=uid)
        req = requests.get(url)
        if req.status_code == 200:
            res = req.json()
            _uid_accounts[uid] = res['account_id']
    return _uid_accounts.get(uid)


def get_account_info(account_id):
    if account_id not in _id_accounts:
        url = _generate_api_url(config.PayAPI.GET_ACCOUNT_INFO_URL, account_id=account_id)
        req = requests.get(url)
        if req.status_code == 200:
            res = req.json()
            _uid_accounts[account_id] = res
    return _uid_accounts.get(account_id)


def get_user_balance(uid):
    account_id = get_account_id(uid)
    url = _generate_api_url(config.PayAPI.GET_USER_BALANCE_URL, account_id=account_id)
    req = requests.get(url)

    if req.status_code == 200:
        data = req.json()
        return data['balance']
    return Decimal(0)


def get_user_cash_records(uid, q, side, tp, page_no=1, page_size=20):
    account_id = get_account_id(uid)
    url = _generate_api_url(config.PayAPI.GET_USER_CASH_RECORDS_URL, account_id=account_id)
    url = build_url(url, q=q, side=side, tp=tp, page_no=page_no, page_size=page_size)

    req = requests.get(url)

    if req.status_code == 200:
        data = req.json()
        return data


def list_trade_orders(uid, category, page_no, page_size, keyword):
    account_id = get_account_id(uid)
    url = _generate_api_url(config.PayAPI.GET_USER_ORDERS_URL, account_id=account_id)

    params = {
        'category': category,
        'page_no': page_no,
        'page_size': page_size
    }
    if keyword:
        params['keyword'] = keyword

    url = build_url(url, **params)

    req = requests.get(url)

    if req.status_code == 200:
        data = req.json()
        return data
