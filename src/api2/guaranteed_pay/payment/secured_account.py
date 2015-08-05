# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from api2.account import new_account
from ._dba import find_secured_account_id, cache_secured_account_id
from pytoolbox.util.dbe import transactional

_SECURED_ACCOUNTS_USER_ID = 0

_secured_account_id = None


def get_secured_account_id(client_id):
    global _secured_account_id

    if _secured_account_id:
        return _secured_account_id

    account_id = find_secured_account_id(client_id)
    if account_id:
        return _cache_secured_account_id(account_id)

    return _cache_secured_account_id(_create_secured_account(client_id))


def _cache_secured_account_id(account_id):
    global _secured_account_id

    _secured_account_id = account_id
    return _secured_account_id


@transactional
def _create_secured_account(client_id):
    account_id = new_account(client_id, _SECURED_ACCOUNTS_USER_ID)
    cache_secured_account_id(client_id, account_id)
    return account_id