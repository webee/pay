# coding=utf-8
from __future__ import unicode_literals

from . import vas_entry_mod as mod
from .. import user
from api_x.utils import response
from api_x.utils.entry_auth import verify_request


@mod.route('/account_users/<account_user_id>/balance', methods=['GET'])
@verify_request('query_account_user_balance')
def query_account_user_balance(account_user_id):
    account_user = user.get_account_user(account_user_id)
    if not account_user:
        return response.not_found(code=404, msg='account user not found: [{0}]'.format(account_user_id))

    balance = user.get_user_cash_balance(account_user_id)
    return response.success(data={'total': balance.total,
                                  'available': balance.available,
                                  'frozen': balance.frozen})
