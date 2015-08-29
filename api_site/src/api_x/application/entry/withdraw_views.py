# coding=utf-8
from __future__ import unicode_literals
from decimal import Decimal

from api_x.utils import response
from api_x.utils.entry_auth import verify_request
from flask import request
from .. import dba
from ..withdraw import apply_to_withdraw, calc_user_withdraw_fee, log_user_withdraw
from . import application_mod as mod
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


@mod.route('/users/<user_id>/withdraw', methods=['POST'])
@verify_request('app_withdraw')
def app_withdraw(user_id):
    data = request.values
    channel = request.channel
    bankcard_id = data['bankcard_id']
    amount = data['amount']
    client_notify_url = data.get('notify_url', '')

    user_map = channel.get_user_map(user_id)
    if user_map is None:
        return response.bad_request(msg='user not exists: [{0}]'.format(user_id))
    from_user_id = user_map.account_user_id

    try:
        amount_value = Decimal(amount)
    except Exception as e:
        logger.error('bad amount value: [{0}]: {1}'.format(amount, e.message))
        return response.bad_request(msg='amount value error: [{0}]'.format(amount))

    fee = calc_user_withdraw_fee(from_user_id, amount_value)

    try:
        bankcard = dba.query_bankcard_by_id(bankcard_id)
        if bankcard is None:
            return response.fail(msg='bankcard not found: [{0}]'.format(bankcard_id))
        if bankcard.user_id != from_user_id:
            return response.fail(msg='bankcard [{0}] is not bound to user [{1}]'.format(bankcard_id, from_user_id))

        tx_sn = apply_to_withdraw(channel, from_user_id, bankcard, amount_value, fee, client_notify_url, data)
        log_user_withdraw(from_user_id, tx_sn, bankcard_id, amount, fee)
        return response.success(sn=tx_sn)
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)
