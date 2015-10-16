# coding=utf-8
from __future__ import unicode_literals, print_function

from flask import request, jsonify
from . import main_mod as mod
import requests
from test_pay_site.main.commons import generate_sn
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


@mod.route('/app_pay', methods=['POST'])
def app_pay():
    data = request.values
    merchant_id = data['merchant_id']
    order_no = data['order_no']

    sn = generate_sn(merchant_id, order_no)

    return jsonify(sn=sn)


@mod.route('/app_do_pay', methods=['POST'])
def app_do_pay():
    # 这里由于没有session， 所以参数全部由客户端传送
    data = request.values
    sn = data['sn']
    result = data['result']
    amount = data['amount']
    notify_url = data['notify_url']
    order_no = data['order_no']

    params = {
        'sn': sn,
        'result': result,
        'order_no': order_no,
        'amount': amount
    }

    # TODO: async notify
    try:
        logger.info('notify {0}: {1}'.format(notify_url, params))
        req = requests.post(notify_url, params)
        print(req.json())
    except Exception as e:
        print(e.message)

    return jsonify(data=params)
