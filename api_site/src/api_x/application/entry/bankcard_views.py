# coding=utf-8
from __future__ import unicode_literals
from api_x.utils import response

from flask import request
from . import application_mod as mod
from .. import dba
from .. import bankcard
from api_x.utils.parser import to_bool
from tools.mylog import get_logger

logger = get_logger(__name__)


@mod.route('/bankcard/<card_no>/bin', methods=['GET'])
def query_bin(card_no):
    try:
        # 缓存bankcard_bin信息
        bankcard_bin = dba.get_bankcard_bin(card_no)
        if bankcard_bin is None:
            bankcard_bin = bankcard.query_bin(card_no)
            dba.add_bankcard_bin(bankcard_bin)
        card_bin_info = bankcard_bin.to_dict()
        return response.success(**card_bin_info)
    except Exception as e:
        logger.exception(e)
        return response.bad_request(msg=e.message)


@mod.route('/account_users/<int:account_user_id>/bankcards', methods=['POST'])
def add_bankcard(account_user_id):
    data = request.values
    card_no = data['card_no']
    acct_name = data['account_name']
    is_corporate_account = to_bool(data['is_corporate_account'])
    province_code = data['province_code']
    city_code = data['city_code']
    brabank_name = data['branch_bank_name']

    bankcard_id = bankcard.add_bankcard(account_user_id, card_no, acct_name, is_corporate_account,
                                        province_code, city_code, brabank_name)
    return response.success(id=bankcard_id)


@mod.route('/account_users/<int:account_user_id>/bankcards', methods=['GET'])
def list_user_bankcards(account_user_id):
    bankcards = dba.query_all_bankcards(account_user_id)
    bankcards = [bankcard.to_dict() for bankcard in bankcards]
    return response.success(bankcards=bankcards)
