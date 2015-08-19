# coding=utf-8
from __future__ import unicode_literals

from flask import request, jsonify
from . import application_mod as mod


@mod.route('/account_users/<int:account_user_id>/bankcards', methods=['GET'])
def list_all_bankcards(account_user_id):
    return jsonify(account_user_id=account_user_id)


@mod.route('/account_users/<int:account_user_id>/bankcards', methods=['POST'])
def add_bankcard(account_user_id):
    data = request.values
    card_no = data['card_no']
    account_name = data['account_name']
    is_corporate_account = to_bool(data['is_corporate_account'])
    province_code = data['province_code']
    city_code = data['city_code']
    branch_bank_name = data['branch_bank_name']

    try:
        bankcard_id = _add_bankcard(account_id, card_no, account_name, is_corporate_account, province_code, city_code,
                                    branch_bank_name)
        return response.created(bankcard_id)
    except ZytCoreError, e:
        return response.bad_request(e.message, card_no=card_no)

# TODO
# withdraw, 手续费控制策略在这里