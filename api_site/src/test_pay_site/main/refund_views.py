# coding=utf-8
from __future__ import unicode_literals, print_function

from flask import request, jsonify
from . import main_mod as mod
import requests
from .commons import generate_sn
from tools.mylog import get_logger
import time
import thread


logger = get_logger(__name__)


@mod.route('/refund', methods=['POST'])
def refund():
    data = request.values
    merchant_id = data['merchant_id']
    refund_no = data['refund_no']
    pay_sn = data['pay_sn']
    amount = data['amount']
    notify_url = data['notify_url']
    result = data['result']

    # find payment by pay_sn
    # do refund
    # notify.
    # ...
    params = {
        'sn': generate_sn(merchant_id, refund_no),
        'result': result,
        'refund_no': refund_no,
    }

    # async notify
    thread.start_new(notify_client, (notify_url, params))

    # 返回成功，通知错误
    params = {
        'sn': params['sn'],
        'result': 'SUCCESS',
        'refund_no': refund_no
    }
    return jsonify(params)


def notify_client(notify_url, params):
    logger.info('before notify: {0}'.format(notify_url))
    time.sleep(2)

    logger.info('start notify: {0}'.format(notify_url))
    try:
        logger.info('notify {0}: {1}'.format(notify_url, params))
        req = requests.post(notify_url, params)
        print(req.json())
    except Exception as e:
        print(e.message)
