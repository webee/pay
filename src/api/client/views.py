# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

from api.util import response
from . import client_mod as mod
from api.account.account import get_cash_balance
from api.account.account.dba import get_account


log = logging.getLogger(__name__)


@mod.route('/<int:client_id>/users/<user_id>/account', methods=['GET'])
def get_account_info(client_id, user_id):
    account = get_account(client_id, user_id)
    if not account:
        response.not_found({'client_id': client_id, 'user_id': user_id})

    account_id = account['id']
    balance = get_cash_balance(account_id)
    return response.ok(account_id=account_id, balance=balance)
