# coding=utf-8
from __future__ import unicode_literals

from flask import request, jsonify, render_template
from . import test_pay_entry_mod as mod
from api_x.zyt.evas.test_pay.constant import BizType, NotifyType
from api_x.zyt.evas.test_pay.notify import get_notify_handle
from api_x.zyt.evas.test_pay import NAME


@mod.route("/pay/result/<pay_source>", methods=["POST"])
def pay_result(pay_source):
    """支付页面回调, 更多操作可由notify完成，这里只是返回callback"""
    data = request.values
    order_no = data['order_no']
    vas_order_no = data['sn']
    result = data['result']
    # TODO: check

    handle = get_notify_handle(pay_source, BizType.PAY, NotifyType.Pay.SYNC)
    if handle:
        # 是否成功，订单号，来源系统，来源系统订单号，数据
        return handle(is_success_result(result), order_no, NAME, vas_order_no, data)

    if is_success_result(result):
        return render_template('info.html', title='支付结果', msg='支付成功(来源未知)-订单号:{0}'.format(order_no))
    return render_template('info.html', title='支付结果', msg='支付失败(来源未知)-订单号:{0}'.format(order_no))


@mod.route("/pay/notify/<pay_source>", methods=["POST"])
def pay_notify(pay_source):
    data = request.values
    order_no = data['order_no']
    vas_order_no = data['sn']
    result = data['result']
    # TODO: check.

    handle = get_notify_handle(pay_source, BizType.PAY, NotifyType.Pay.ASYNC)
    if handle:
        # 是否成功，订单号，来源系统，来源系统订单号，数据
        if handle(is_success_result(result), order_no, NAME, vas_order_no, data):
            return jsonify(code=0)

    return jsonify(code=1)


def is_success_result(result):
    return result == 'SUCCESS'
