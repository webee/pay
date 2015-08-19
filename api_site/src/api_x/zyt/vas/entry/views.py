# coding=utf-8
from __future__ import unicode_literals

from . import vas_entry_mod as mod
from .. import user
from api_x.utils import response


@mod.route('/account_users/<account_user_id>/balance', methods=['GET'])
def account_user_balance(account_user_id):
    account_user = user.get_user_by_id(account_user_id)
    if not account_user:
        return response.fail(code=404, msg='account user not found: [{0}]'.format(account_user_id)), 404

    balance = user.get_user_cash_balance(account_user_id)
    return response.success(total=balance.total, available=balance.available, frozen=balance.frozen)
