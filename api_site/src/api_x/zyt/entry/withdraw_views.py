# coding=utf-8
from __future__ import unicode_literals
from decimal import Decimal

from api_x.utils import response
from flask import request
from . import biz_entry_mod as mod
from pytoolbox.util.log import get_logger
from api_x.utils.entry_auth import verify_request, _register_api_entry
from api_x.zyt.biz import withdraw

logger = get_logger(__name__)


@mod.route('/users/<user_id>/withdraw', methods=['POST'])
@verify_request('withdraw')
def apply_to_withdraw(user_id):
    data = request.values
    channel = request.channel
    # bankcard info
    flag_card = data['flag_card']
    card_type = data['card_type']
    card_no = data['card_no']
    acct_name = data['acct_name']
    bank_code = data.get('bank_code')
    province_code = data.get('province_code')
    city_code = data.get('city_code')
    bank_name = data['bank_name']
    brabank_name = data.get('brabank_name')
    prcptcd = data.get('prcptcd')

    amount = data['amount']
    fee = data['fee']
    client_notify_url = data['notify_url']

    user_map = channel.get_user_map(user_id)
    if user_map is None:
        return response.bad_request(msg='user not exists: [{0}]'.format(user_id))
    from_user_id = user_map.account_user_id

    try:
        amount_value = Decimal(amount)
        fee_value = Decimal(fee)
    except Exception as e:
        logger.exception(e)
        return response.bad_request(msg=e.message)

    try:
        withdraw_record = withdraw.apply_to_withdraw(channel, from_user_id,
                                                     flag_card, card_type, card_no, acct_name, bank_code, province_code,
                                                     city_code, bank_name, brabank_name, prcptcd,
                                                     amount_value, fee_value, client_notify_url, data)
        return response.success(sn=withdraw_record.sn)
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)
