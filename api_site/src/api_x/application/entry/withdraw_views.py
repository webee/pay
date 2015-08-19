# coding=utf-8
from __future__ import unicode_literals
from decimal import Decimal

from flask import request
from .. import dba
from ..withdraw import apply_to_withdraw, calc_user_withdraw_fee, log_user_withdraw
from . import application_mod as mod
from api_x.util import response
from tools.mylog import get_logger


logger = get_logger(__name__)


@mod.route('/account_users/<int:account_user_id>/withdraw', methods=['POST'])
def withdraw(account_user_id):
    data = request.values
    bankcard_id = data['bankcard_id']
    amount = data['amount']
    client_notify_url = data.get('notify_url', '')

    try:
        amount_value = Decimal(amount)
    except Exception as e:
        logger.error('bad amount value: [{0}]: {1}'.format(amount, e.message))
        return response.bad_request(msg='amount value error: [{0}]'.format(amount))

    fee = calc_user_withdraw_fee(account_user_id, amount_value)

    try:
        bankcard = dba.query_bankcard_by_id(bankcard_id)
        if bankcard is None:
            return response.fail(msg='bankcard not found: [{0}]'.format(bankcard_id))
        if bankcard.user_id != account_user_id:
            return response.fail(msg='bankcard [{0}] is not bound to user [{1}]'.format(bankcard_id, account_user_id))

        tx_sn = apply_to_withdraw(account_user_id, bankcard, amount_value, fee, client_notify_url, data)
        log_user_withdraw(account_user_id, tx_sn, bankcard_id, amount, fee)
        return response.success(sn=tx_sn)
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)


@mod.route('/account_users/<int:account_user_id>/withdraw/notify', methods=['POST'])
def withdraw_notify(account_user_id):
    data = request.values

    return "OK"
