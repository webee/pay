# coding=utf-8
from __future__ import unicode_literals
from decimal import Decimal

from flask import request
from api_x.utils import response
from api_x.utils.entry_auth import verify_request
from api_x.zyt.biz.transaction.dba import get_tx_by_sn
from api_x.constant import WithdrawTxState
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
    order_id = data.get('order_id')
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

        withdraw_record = apply_to_withdraw(channel, order_id, from_user_id, bankcard, amount_value, fee, client_notify_url, data)
        log_user_withdraw(from_user_id, withdraw_record.sn, bankcard_id,
                          withdraw_record.amount, withdraw_record.actual_amount, withdraw_record.fee)
        return response.success(sn=withdraw_record.sn,
                                actual_amount=withdraw_record.actual_amount, fee=withdraw_record.fee)
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)


@mod.route('/users/<user_id>/withdraw/<sn>', methods=['GET'])
@verify_request('app_query_withdraw')
def app_query_withdraw(user_id, sn):
    data = request.values
    channel = request.channel

    user_map = channel.get_user_map(user_id)
    if user_map is None:
        return response.bad_request(msg='user not exists: [{0}]'.format(user_id))
    from_user_id = user_map.account_user_id

    tx = get_tx_by_sn(sn)
    if tx is None:
        return response.not_found(msg="withdraw tx not exits: [sn: {0}]".format(sn))
    withdraw_record = tx.record

    if withdraw_record.from_user_id != from_user_id:
        return response.bad_request('user [{0}] has no withdraw [{1}]'.format(user_id, sn))

    if tx.state == WithdrawTxState.SUCCESS:
        code = 0
    elif tx.state == WithdrawTxState.FAILED:
        code = 1
    else:
        code = 2

    params = {'code': code,
              'user_id': user_id,
              'sn': tx.sn,
              'amount': withdraw_record.amount,
              'actual_amount': withdraw_record.actual_amount,
              'fee': withdraw_record.fee}

    return response.success(data=params)
