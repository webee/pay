# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

import json

from flask import request, jsonify
from . import account_mod as mod
from .bankcard import *
from tools.lock import require_user_account_locker
from .withdraw import NoBankcardFoundError, AmountValueError, AmountNotPositiveError, InsufficientBalanceError
from .withdraw import WithDrawFailedError
from .withdraw import withdraw_transaction, get_withdraw_order, get_frozen_withdraw_order
from .withdraw import is_successful_result, fail_withdraw, succeed_withdraw
from api.util import response
from api.util.ipay.transaction import notification
from api.util.ipay.transaction import parse_and_verify, is_valid_transaction
from api.util.parser import to_bool
from tools.mylog import get_logger
from tools.utils import to_float

logger = get_logger(__name__)


@mod.route('/<int:account_id>/withdraw', methods=['POST'])
def withdraw(account_id):
    """ 提现接口
    POST: bankcard_id, amount, callback_url
    :type account_id: unicode or int
    :return:
    """
    req_data = request.values
    bankcard_id = req_data.get('bankcard_id')
    callback_url = req_data.get('callback_url')
    amount = req_data.get('amount')

    try:
        order_id = withdraw_transaction(account_id, bankcard_id, amount, callback_url)
        return response.accepted(order_id)
    except NoBankcardFoundError as e:
        return response.bad_request(e.message)
    except AmountValueError as e:
        return response.bad_request(e.message)
    except AmountNotPositiveError as e:
        return response.bad_request(e.message)
    except InsufficientBalanceError as e:
        return response.bad_request(e.message)
    except WithDrawFailedError as e:
        return response.created(e.order_id)


@mod.route('/withdraw/<uuid>/result', methods=['POST'])
@parse_and_verify
def notify_withdraw(uuid):
    data = request.verified_data
    logger.info(json.dumps(data))

    oid_partner = data['oid_partner']
    order_id = data['no_order']
    if not is_valid_transaction(oid_partner, order_id, uuid):
        return notification.is_invalid()

    with require_user_account_locker(order_id, 'cash') as _:
        amount = to_float(data['money_order'])
        withdraw_order = get_frozen_withdraw_order(order_id, amount)
        if withdraw_order is None:
            notification.is_invalid()

        # dt_order = data['dt_order']
        paybill_id = data['oid_paybill']
        failure_info = data.get('info_order', '')
        result = data['result_pay']
        settle_date = data.get('settle_date', '')

        if not is_successful_result(result):
            fail_withdraw(withdraw_order, paybill_id, failure_info)
            return notification.fail()

        succeed_withdraw(withdraw_order, paybill_id, settle_date)
        return notification.succeed()


@mod.route('/<int:account_id>/bankcards', methods=['GET'])
def list_all_bankcards(account_id):
    bankcards = list_all_bankcards(account_id)
    return json.dumps(bankcards), 200


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


@mod.route('/test', methods=['POST'])
def test():
    data = {k: v for k, v in request.values.items()}
    logger.info(json.dumps(data))

    return jsonify(data)
