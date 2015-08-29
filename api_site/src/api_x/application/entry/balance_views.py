# coding=utf-8
from __future__ import unicode_literals
from api_x.utils import response
from api_x.utils.entry_auth import verify_request

from flask import request
from . import application_mod as mod
from .. import account_user
from pytoolbox.util.log import get_logger

logger = get_logger(__name__)


@mod.route('/users/<user_id>/bankcards', methods=['POST'])
@verify_request('app_query_user_balance')
def query_user_balance(user_id):
    channel = request.channel

    user_map = channel.get_user_map(user_id)
    if user_map is None:
        return response.bad_request(msg='user not exists: [{0}]'.format(user_id))
    account_user_id = user_map.account_user_id

    balance = account_user.get_user_cash_balance(account_user_id)
    return response.success(data={'total': balance.total,
                                  'available': balance.available,
                                  'frozen': balance.frozen})
