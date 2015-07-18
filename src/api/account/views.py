# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

import json

from flask import request, current_app
from . import account
from . import account_mod as mod
from .bankcard import list_all_bankcards, get_bankcard, new_bankcard, BankCard
from tools.utils import to_int, to_float
from .withdraw import create_withdraw_order_and_freeze_cash, get_withdraw_order, withdraw_request_failed, withdraw_order_end
from api.util import response
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
    req_data = request.values
    bankcard_id = to_int(req_data.get('bankcard_id'))
    callback_url = req_data.get('callback_url')

    bankcard = get_bankcard(account_id, bankcard_id)
    if bankcard is None:
        return resp.FALSE_BANKCARD_NOT_EXISTS

    amount = to_float(req_data.get('amount'))
    if amount <= 0:
        return resp.FALSE_AMOUNT_VALUE_ERROR

    # TODO: 从这开始加锁，同时只能有一个在执行操作account_id的cash账户
    balance = account.get_cash_balance(account_id)
    if amount > balance:
        return resp.FALSE_INSUFFICIENT_BALANCE

    order_info = "提现"
    host_url = current_app.config.get('HOST_URL')

    # 1. 生成提现订单并冻结金额
    order_id = create_withdraw_order_and_freeze_cash(account_id, bankcard.id, amount, callback_url)
    if order_id is None:
        return resp.FALSE_ERROR_CREATING_ORDER
    # TODO: 这里要释放锁

    # 3. 发送请求
    notify_url = host_url + transaction.generate_pay_to_bankcard_notification_url(order_id)
    res_data = transaction.pay_to_bankcard(order_id, amount, order_info, notify_url, bankcard)

    logger.info(json.dumps(res_data))

    if res_data['ret']:
        return resp.TRUE_JUST_OK

    try:
        withdraw_request_failed(order_id)
    except Exception as e:
        # TODO: do something.
        logger.error(e.message)
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

    withdraw_order_end(withdraw_order, paybill_id, result, failure_info, settle_date)

    return pay_resp.SUCCESS


@mod.route('/<int:account_id>/bankcards', methods=['GET'])
def list_all_bankcards(account_id):
    bankcards = list_all_bankcards(account_id)
    return json.dumps(bankcards), 200


@mod.route('/<int:account_id>/bankcards', methods=['POST'])
def add_bankcard(account_id):
    data = request.values
    card_no = data['card_no']
    account_name = data['account_name']
    is_corporate_account = bool(data['is_corporate_account'])
    bank_code = data['bank_code']
    province_code = data['province_code']
    city_code = data['city_code']
    branch_bank_name = data['branch_bank_name']

    card = BankCard(card_no, account_name, is_corporate_account, bank_code, province_code, city_code, branch_bank_name)
    bankcard_id = new_bankcard(account_id, card)
    return response.created(bankcard_id)
