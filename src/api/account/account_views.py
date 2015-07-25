# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from . import account_mod as mod
from . import account
from .account import dba
from api.util import response
from tools.mylog import get_logger

logger = get_logger(__name__)


@mod.route('/<int:account_id>/balance', methods=['GET'])
def balance(account_id):
    if dba.user_account_exists(account_id):
        return response.not_found()

    balance = account.get_cash_balance(account_id)
    return response.ok(balance=balance)
