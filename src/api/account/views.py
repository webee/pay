# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

import json

from flask import request, jsonify, current_app, url_for
from . import account_mod as mod
from api.account.bankcard import get_user_bankcards, get_bankcard
from tools.utils import to_int, to_float
from .withdraw import create_withdraw_order, get_withdraw_order, withdraw_request_fail, withdraw_order_end
from .withdraw import freeze_withdraw_cash
from api.util.ipay import transaction
from tools.mylog import get_logger

logger = get_logger(__name__)


@mod.route('/<int:account_id>/withdraw', methods=['POST'])
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
        return jsonify(ret=False, msg="此银行卡不存在")

    amount = to_float(data.get('amount'))
    if amount <= 0:
        return jsonify(ret=False, msg="[amount]错误")
    # TODO: 获取余额, 检查余额是否足够
    order_info = "提现"
    host_url = current_app.config.get('HOST_URL')
    notify_url = host_url + url_for('account.withdraw_notify')

    # 1. 生成提现订单
    order_id = create_withdraw_order(account_id, bankcard.id, amount, callback_url)
    # 2. 冻结金额
    freeze_withdraw_cash(account_id, order_id, amount)
    # 3. 发送请求
    data = transaction.pay_to_bankcard(order_id, amount, order_info, notify_url, bankcard)

    logger.info(json.dumps(data))

    if data['ret']:
        return jsonify(ret=True)

    withdraw_request_fail(order_id)
    return jsonify(ret=False, msg="请求失败")


@mod.route('/withdraw_notify', methods=['POST'])
def withdraw_notify():
    raw_data = request.data

    data = transaction.parse_request_data(raw_data)
    logger.info(json.dumps(data))

    partner_id = data['oid_partner']
    if transaction.is_sending_to_me(partner_id):
        return jsonify(ret_code='9999', ret_msg='发送错误')

    order_id = data['no_order']
    withdraw_order = get_withdraw_order(order_id)
    if withdraw_order is None:
        return jsonify(ret_code='9999', ret_msg='订单不存在')

    # dt_order = data['dt_order']

    money_order = to_float(data['money_order'])
    if money_order != withdraw_order['amount']:
        return jsonify(ret_code='9999', ret_msg='订单金额不正确')

    paybill_id = data['oid_paybill']
    failure_info = data.get('info_order', '')
    result = data['result_pay']
    settle_date = data.get('settle_date', '')

    withdraw_order_end(order_id, paybill_id, result, failure_info, settle_date)

    return jsonify(ret_code='0000', ret_msg='交易成功')


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
