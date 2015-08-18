# coding=utf-8
from __future__ import unicode_literals

from flask import request, jsonify
from . import test_pay_entry_mod as mod
from api_x.zyt.evas.test_pay.notify import get_refund_notify_handle
from api_x.zyt.evas.test_pay import NAME


@mod.route("/refund/notify/<refund_source>", methods=["POST"])
def refund_notify(refund_source):
    data = request.values
    result = data['result']
    refund_no = data['refund_no']
    vas_order_no = data['sn']

    handle = get_refund_notify_handle(refund_source)
    if handle:
        # 是否成功，订单号，来源系统，来源系统订单号，数据
        if handle(is_success_result(result), refund_no, NAME, vas_order_no, data):
            return jsonify(code=0)

    return jsonify(code=1)


def is_success_result(result):
    return result == 'SUCCESS'
