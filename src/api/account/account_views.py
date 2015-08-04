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
    if not dba.user_account_exists(account_id):
        return response.not_found()

    balance = account.get_cash_balance(account_id)
    return response.ok(balance=balance)


@mod.route('/<int:user_domain_id>/<int:user_id>/balance', methods=['GET'])
def user_balance(user_domain_id, user_id):
    user_account = dba.get_account_by_user_id(user_domain_id, user_id)
    if user_account is None:
        return response.not_found()

    balance = account.get_cash_balance(user_account.id)
    return response.ok(balance=balance)
