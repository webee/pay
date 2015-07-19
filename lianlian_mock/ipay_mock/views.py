# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

import json
import random
from datetime import datetime

from flask import request

from . import ipay_mock_mod as mod
from api.util.ipay import transaction
from tools.mylog import get_logger
from api.util.ipay.constant import response as pay_resp
from lianlian_mock import pay_tasks

logger = get_logger(__name__)


def now_date_str():
    return datetime.now().strftime('%Y%m%d')


@mod.route('/cardandpay', methods=['POST'])
def cardandpay():
    raw_data = request.data

    data = transaction.parse_request_data(raw_data)
    logger.info(json.dumps(data, ensure_ascii=False))

    req_data = data

    notify_url = req_data['notify_url']
    params = {
        'oid_partner': req_data['oid_partner'],
        'no_order': req_data['no_order'],
        'dt_order': req_data['dt_order'],
        'money_order': req_data['money_order'],
        'oid_paybill': _generate_id(random.randint(1, 1000000)),
        'result_pay': 'SUCCESS',
        'settle_date': now_date_str()
    }
    pay_tasks.mock_notify.delay(notify_url, transaction.md5_sign_params(params), delay=10)

    return transaction.md5_sign_params({'ret_code': '0000', 'ret_msg': '交易成功'})


@mod.route('/notify_test', methods=['POST'])
def notify_test():
    raw_data = request.data

    data = transaction.parse_request_data(raw_data)
    logger.info(json.dumps(data, ensure_ascii=False))
    return pay_resp.SUCCESS



def _generate_id(base_id):
    return 'LPB' + datetime.now().strftime("%Y%m%d%H%M%S%f") + '%0.7d' % base_id