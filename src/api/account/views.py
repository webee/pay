# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

import json
from flask import request, jsonify
from . import account_mod as mod
from .entities import get_bank_card
from tools.utils import to_int
from . import test
from api import lianlian_service as service
import requests
from api.base_config import use_config
from .withdraw import config

log = logging.getLogger(__name__)


@mod.route('/<account_id>/withdraw', methods=['POST'])
def withdraw(account_id):
    data = request.form
    bankcard_id = to_int(data.get('bankcard_id', ''))

    bankcard = get_bank_card(account_id, bankcard_id)

    money_order = data.get('amount')
    no_order = test.get_current_datetime_str()
    info_order = "提款"
    notify_url = ""

    with use_config(config):
        data = service.withdraw(no_order, money_order, info_order, notify_url, bankcard)

    if data['ret']:
        return jsonify(ret=True)
    return jsonify(ret=False, msg="请求失败")


@mod.route('/<int:account_id>/bankcards', methods=['GET'])
def list_all(account_id):
    bankcards = bankcard.list_all(account_id)
    return json.dumps(bankcards), 200
