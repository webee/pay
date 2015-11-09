# coding=utf-8
from __future__ import unicode_literals

from flask import request
from . import vas_entry_mod as mod
from .. import user
from api_x.utils import response
from api_x.utils.entry_auth import verify_request
from pytoolbox.util.log import get_logger
from api_x.zyt.vas import pay
from api_x.zyt.biz.transaction.dba import get_tx_by_sn

logger = get_logger(__name__)


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


@mod.route('/pay', methods=['POST'])
@verify_request('zyt_pay')
def zyt_pay():
    data = request.params
    channel = request.channel

    if not channel.zyt_pay_enabled:
        return response.refused(msg="zyt pay is not allowed for channel [{0}]".format(channel.name))

    sn = data['sn']
    tx = get_tx_by_sn(sn)
    if tx is None:
        return response.not_found()

    payer_user_id = data['payer_user_id']
    payer_user_map = channel.get_user_map(payer_user_id)
    if payer_user_map is None:
        return response.not_found()

    try:
        is_success = pay(tx.type, sn, payer_user_map.account_user_id, tx.amount)
        return response.success(is_success=is_success)
    except Exception as e:
        logger.exception(e)
    return response.error()
