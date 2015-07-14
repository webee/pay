# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

import json
from flask import request, jsonify
from . import account_mod as mod
from .entities import get_user_bankcards, get_bankcard
from tools.utils import to_int
from . import test
from api import lianlian_service as service
from api.base_config import use_config
from .withdraw import config

log = logging.getLogger(__name__)


@mod.route('/<int:account_id>/withdraw', methods=['GET'])
def withdraw(account_id):
    data = request.args
    bankcard_id = to_int(data.get('bankcard_id'))

    bankcard = get_bankcard(account_id, bankcard_id)

    money_order = data.get('amount')
    no_order = test.get_current_datetime_str()
    info_order = "提款"
    notify_url = "www.sina.com"
    # TODO: 新建提现订单

    with use_config(config):
        data = service.withdraw(no_order, money_order, info_order, notify_url, bankcard)

    if data['ret']:
        return jsonify(ret=True)
    return jsonify(ret=False, msg="请求失败")


@mod.route('/<int:account_id>/bankcards', methods=['GET'])
def list_all(account_id):
    bankcards = get_user_bankcards(account_id)
    return jsonify(
        ret=True,
        bankcards=bankcards
    )
