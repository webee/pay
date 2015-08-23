# coding=utf-8
from __future__ import unicode_literals
from decimal import Decimal

from api_x.utils import response
from flask import request
from . import biz_entry_mod as mod
from pytoolbox.util.log import get_logger
from api_x.utils.entry_auth import verify_request
from api_x.zyt.biz import withdraw

logger = get_logger(__name__)


@mod.route('/withdraw', methods=['POST'])
@verify_request('withdraw')
def apply_to_withdraw():
    data = request.values
    channel = request.channel
    from_user_id = data['from_user_id']
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

    logger.info('receive withdraw: {0}'.format({k: v for k, v in data.items()}))

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
