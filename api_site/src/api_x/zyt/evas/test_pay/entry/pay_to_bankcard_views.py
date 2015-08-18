# coding=utf-8
from __future__ import unicode_literals

from flask import request, jsonify
from . import test_pay_entry_mod as mod
from api_x.zyt.evas.test_pay.notify import get_pay_to_bankcard_notify_handle
from api_x.zyt.evas.test_pay import NAME
from tools.mylog import get_logger


logger = get_logger(__name__)


@mod.route("/pay_to_bankcard/notify/<source>", methods=["POST"])
def pay_to_bankcard_notify(source):
    data = request.datq
    result = data['result']
    order_no = data['order_no']
    vas_sn = data['sn']

    logger.info('pay_to_bankcard notify {0}: {1}'.format(source, data))

    handle = get_pay_to_bankcard_notify_handle(source)
    if handle:
        # 是否成功，订单号，来源系统，来源系统订单号，数据
        handle(is_success_result(result), order_no, NAME, vas_sn, data)
        logger.info('pay_to_bankcard notify success: {0}, {1}'.format(source, order_no))
        return jsonify(code=0)

    return jsonify(code=1)


def is_success_result(result):
    return result == 'SUCCESS'
