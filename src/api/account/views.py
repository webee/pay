# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

import json

from flask import request, jsonify, current_app, url_for
from . import account_mod as mod
from . import accounts
from api.account.bankcard import get_user_bankcards, get_bankcard
from tools.utils import to_int, to_float
from .withdraw import create_withdraw_order, get_withdraw_order, withdraw_request_failed, withdraw_order_end
from .withdraw import freeze_withdraw_cash
from api.util.ipay import transaction
from api.util.api import return_json
from api.constant import response as resp
from api.util.ipay.constant import response as pay_resp
from tools.mylog import get_logger

logger = get_logger(__name__)


@mod.route('/<int:account_id>/withdraw', methods=['POST'])
@return_json
def withdraw(account_id):
    """ 提现接口
    POST: bankcard_id, amount, callback_url
    :type account_id: unicode or int
    :return:
    """
    data = request.values
    bankcard_id = to_int(data.get('bankcard_id'))
    callback_url = data.get('callback_url')

    bankcard = get_bankcard(account_id, bankcard_id)
    if bankcard is None:
        return resp.FALSE_BANKCARD_NOT_EXISTS

    amount = to_float(data.get('amount'))
    if amount <= 0:
        return resp.FALSE_AMOUNT_VALUE_ERROR
    balance = accounts.cash_account_balance(account_id)
    if amount > balance:
        return resp.FALSE_INSUFFICIENT_BALANCE

    order_info = "提现"
    host_url = current_app.config.get('HOST_URL')
    notify_url = host_url + url_for('account.notify_withdraw', uuid=transaction.encode_uuid(order_id))

    # 1. 生成提现订单
    order_id = create_withdraw_order(account_id, bankcard.id, amount, callback_url)
    # 2. 冻结金额
    freeze_withdraw_cash(account_id, order_id, amount)
    # 3. 发送请求
    data = transaction.pay_to_bankcard(order_id, amount, order_info, notify_url, bankcard)

    logger.info(json.dumps(data))

    if data['ret']:
        return resp.TRUE_JUST_OK

    withdraw_request_failed(order_id)
    return resp.FALSE_REQUEST_FAILED


@mod.route('/withdraw/<uuid>/result', methods=['POST'])
@return_json
def notify_withdraw(uuid):
    raw_data = request.data

    data = transaction.parse_request_data(raw_data)
    logger.info(json.dumps(data))

    oid_partner = data['oid_partner']
    order_id = data['no_order']
    if not transaction.is_valid_transaction(oid_partner, order_id, uuid):
        return pay_resp.INVALID_NOTIFICATION

    amount = to_float(data['money_order'])
    withdraw_order = get_withdraw_order(order_id)
    if withdraw_order is None or amount != withdraw['amount']:
        return pay_resp.INVALID_NOTIFICATION

    # dt_order = data['dt_order']

    paybill_id = data['oid_paybill']
    failure_info = data.get('info_order', '')
    result = data['result_pay']
    settle_date = data.get('settle_date', '')

    withdraw_order_end(order_id, paybill_id, result, failure_info, settle_date)

    return pay_resp.SUCCESS


@mod.route('/<int:account_id>/bankcards', methods=['GET'])
def list_all_bankcards(account_id):
    bankcards = get_user_bankcards(account_id)
    return jsonify(
        ret=True,
        bankcards=bankcards
    )


@mod.route('/<int:account_id>/bankcards', methods=['POST'])
def add_bankcard(account_id):
    data = request.values

    return jsonify(data=data)
