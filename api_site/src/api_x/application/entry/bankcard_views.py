# coding=utf-8
from __future__ import unicode_literals
from api_x.utils import response
from api_x.utils.entry_auth import verify_request

from flask import request
from . import application_mod as mod
from .. import dba
from .. import bankcard
from api_x.utils.parser import to_bool
from pytoolbox.util.log import get_logger

logger = get_logger(__name__)


@mod.route('/bankcard/<card_no>/bin', methods=['GET'])
@verify_request('query_bin')
def query_bin(card_no):
    try:
        # 缓存bankcard_bin信息
        bankcard_bin = dba.get_bankcard_bin(card_no)
        if bankcard_bin is None:
            bankcard_bin = bankcard.query_bin(card_no)
            dba.add_bankcard_bin(bankcard_bin)
        card_bin_info = bankcard_bin.to_dict()
        return response.success(data=card_bin_info)
    except Exception as e:
        logger.exception(e)
        return response.bad_request(msg=e.message)


@mod.route('/users/<user_id>/bankcards', methods=['POST'])
@verify_request('add_bankcard')
def add_bankcard(user_id):
    data = request.params
    channel = request.channel
    card_no = data['card_no']
    acct_name = data['account_name']
    is_corporate_account = to_bool(data['is_corporate_account'])
    province_code = data['province_code']
    city_code = data['city_code']
    brabank_name = data['branch_bank_name']

    user_map = channel.get_user_map(user_id)
    if user_map is None:
        return response.bad_request(msg='user not exists: [{0}]'.format(user_id))
    account_user_id = user_map.account_user_id

    bankcard_id = bankcard.add_bankcard(account_user_id, card_no, acct_name, is_corporate_account,
                                        province_code, city_code, brabank_name)
    return response.success(id=bankcard_id)


@mod.route('/users/<user_id>/bankcards', methods=['GET'])
@verify_request('list_user_bankcards')
def list_user_bankcards(user_id):
    channel = request.channel

    user_map = channel.get_user_map(user_id)
    if user_map is None:
        return response.bad_request(msg='user not exists: [{0}]'.format(user_id))
    account_user_id = user_map.account_user_id

    bankcards = dba.query_all_bankcards(account_user_id)
    bankcards = [bc.to_dict() for bc in bankcards]
    return response.success(data=bankcards)
