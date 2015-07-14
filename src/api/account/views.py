# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

import json
from flask import request, jsonify, current_app, url_for
from . import account_mod as mod
from .entities import get_user_bankcards, get_bankcard
from tools.utils import to_int, to_float
from api import lianlian_service as service
from .withdraw import create_withdraw_order
from tools.mylog import get_logger

logger = get_logger(__name__)


@mod.route('/<int:account_id>/withdraw', methods=['POST'])
def withdraw(account_id):
    """ 提现接口
    POST: bankcard_id, amount
    :type account_id: unicode or int
    :return:
    """
    data = request.values
    bankcard_id = to_int(data.get('bankcard_id'))

    bankcard = get_bankcard(account_id, bankcard_id)
    if bankcard is None:
        return jsonify(ret=False, msg="此银行卡不存在")

    amount = to_float(data.get('amount'))
    if amount <= 0:
        return jsonify(ret=False, msg="[amount]错误")
    order_info = "提现"
    host_url = current_app.config.get('HOST_URL')
    notify_url = host_url + url_for('account.withdraw_notify')

    order_id = create_withdraw_order(account_id, bankcard.id, amount)

    data = service.withdraw(order_id, amount, order_info, notify_url, bankcard)

    logger.info(json.dumps(data))
    if data['ret']:
        return jsonify(ret=True)
    return jsonify(ret=False, msg="请求失败")


@mod.route('/withdraw_notify', methods=['POST'])
def withdraw_notify():
    raw_data = request.data

    data = service.parse_request_data(raw_data)
    # oid_partner
    # no_order
    # dt_order
    # money_order
    # oid_paybill
    # info_order
    # result_pay
    # settle_date
    # TODO: 修改提现订单

    return jsonify(ret_code='0000', ret_msg='交易成功')


@mod.route('/<int:account_id>/bankcards', methods=['GET'])
def list_all(account_id):
    bankcards = get_user_bankcards(account_id)
    return jsonify(
        ret=True,
        bankcards=bankcards
    )
