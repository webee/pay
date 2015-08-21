# coding=utf-8
import os
import requests
from pub_site import config
from decimal import Decimal
from tools.urls import build_url
from pytoolbox.util.log import get_logger


_uid_accounts = {}
_id_accounts = {}

logger = get_logger(__name__)


def _generate_api_url(url, **kwargs):
    url = url.lstrip('/')
    url = os.path.join(config.PayAPI.ROOT_URL, url.format(**kwargs))
    logger.info("request url %s" % url)
    return url


def get_account_user_id(user_id, user_domain_name=config.USER_DOMAIN_NAME):
    if user_id not in _uid_accounts:
        url = _generate_api_url(config.PayAPI.GET_CREATE_ACCOUNT_ID_URL,
                                user_domain_name=user_domain_name, user_id=user_id)
        req = requests.post(url)
        if req.status_code == 200:
            res = req.json()
            _uid_accounts[user_id] = res['account_user_id']
    return _uid_accounts.get(user_id)


def get_user_balance(uid):
    account_user_id = get_account_user_id(uid)
    url = _generate_api_url(config.PayAPI.GET_USER_BALANCE_URL, account_user_id=account_user_id)
    req = requests.get(url)

    if req.status_code == 200:
        data = req.json()
        return data['data']['total'], data['data']['available'], data['data']['frozen']
    return Decimal(0), Decimal(0), Decimal(0)


def get_user_available_balance(uid):
    return get_user_balance(uid)[1]


def list_user_bankcards(uid):
    account_user_id = get_account_user_id(uid)
    url = _generate_api_url(config.PayAPI.LIST_USER_BANKCARDS_URL, account_user_id=account_user_id)
    req = requests.get(url)

    if req.status_code == 200:
        return req.json()['bankcards']
    return []


def get_bin(card_no):
    url = _generate_api_url(config.PayAPI.QUERY_BIN_URL, card_no=card_no)

    req = requests.get(url)
    return req.json()


def query_transactions(uid, role, page_no, page_size, q):
    account_user_id = get_account_user_id(uid)
    url = _generate_api_url(config.PayAPI.GET_USER_TRANSACTIONS_URL, account_user_id=account_user_id)

    params = {
        'role': role,
        'page_no': page_no,
        'page_size': page_size
    }
    if q:
        params['q'] = q

    url = build_url(url, **params)
    req = requests.get(url)

    if req.status_code == 200:
        data = req.json()
        return data
