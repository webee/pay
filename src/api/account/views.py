# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division


from flask import request, jsonify, json
from . import account_mod as mod
from .account import get_cash_balance, user_account_exists
from .bankcard import *
from .withdraw import NoBankcardFoundError, AmountValueError, AmountNotPositiveError, InsufficientBalanceError
from .withdraw import WithDrawFailedError, CreateWithDrawOrderError
from .withdraw import withdraw_transaction, query_withdraw_order
from .withdraw import handle_withdraw_notify
from api.util import response
from api.util.ipay.transaction import notification
from api.util.ipay.transaction import parse_and_verify, is_valid_transaction
from api.util.parser import to_bool
from tools.mylog import get_logger

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
    except CreateWithDrawOrderError as e:
        return response.bad_request(e.message)
    except WithDrawFailedError as e:
        return response.bad_request("第三文支付请求失败", order_id=e.order_id)


@mod.route('/<int:account_id>/withdraw/<order_id>', methods=['GET'])
def query_withdraw(account_id, order_id):
    withdraw_order = query_withdraw_order(account_id, order_id)
    if withdraw_order is None:
        return response.not_found()
    withdraw_order = dict(withdraw_order)
    withdraw_order['amount'] = float(withdraw_order['amount'])
    withdraw_order.pop('paybill_id')
    withdraw_order.pop('settle_date')
    return jsonify(withdraw_order)


@mod.route('/withdraw/<uuid>/result', methods=['POST'])
@parse_and_verify
def notify_withdraw(uuid):
    data = request.verified_data
    logger.info(json.dumps(data))

    oid_partner = data['oid_partner']
    order_id = data['no_order']
    if not is_valid_transaction(oid_partner, order_id, uuid):
        return notification.is_invalid()

    return handle_withdraw_notify(order_id, data)


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


@mod.route('/<int:account_id>/balance', methods=['GET'])
def balance(account_id):
    if not user_account_exists(account_id):
        return response.not_found()
    balance = get_cash_balance(account_id)
    return response.ok(balance=balance)
