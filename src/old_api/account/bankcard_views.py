# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import request
from . import account_mod as mod
from .bankcard import *
from old_api.util import response
from old_api.util.parser import to_bool
from tools.mylog import get_logger

logger = get_logger(__name__)


@mod.route('/<int:account_id>/bankcards', methods=['GET'])
def list_all_bankcards(account_id):
    bankcards = query_all_bankcards(account_id)
    bankcards = [dict(bankcard) for bankcard in bankcards]
    return response.list_data(bankcards)


@mod.route('/<int:account_id>/bankcards', methods=['POST'])
def add_bankcard(account_id):
    data = request.values
    card_no = data['card_no']
    account_name = data['account_name']
    is_corporate_account = to_bool(data['is_corporate_account'])
    province_code = data['province_code']
    city_code = data['city_code']
    branch_bank_name = data['branch_bank_name']

    card = BankCard.query(card_no)
    if card is None:
        return response.bad_request("Invalid bank card.", card_no=card_no)

    card.set_details(account_name, is_corporate_account, province_code, city_code, branch_bank_name)

    if card.is_not_using_debit_card_as_private_account:
        return response.bad_request("The bank card must be a Debit Card if it was added as private account.",
                                    card_no=card_no, is_corporate_account=is_corporate_account)

    bankcard_id = new_bankcard(account_id, card)
    return response.created(bankcard_id)

