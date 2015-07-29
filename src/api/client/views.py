# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

from api.util import response
from . import client_mod as mod
from api.account.account import get_cash_balance
from api.account.account.dba import get_account


log = logging.getLogger(__name__)


@mod.route('/<int:client_id>/users/<user_id>/balance', methods=['GET'])
def get_balance(client_id, user_id):
    account = get_account(client_id, user_id)
    if not account:
        response.not_found({'client_id':client_id, 'user_id':user_id})

    balance = get_cash_balance(account['id'])
    return response.ok(balance=balance)
