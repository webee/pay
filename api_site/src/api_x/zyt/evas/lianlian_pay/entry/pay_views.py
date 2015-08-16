# coding=utf-8
from __future__ import unicode_literals

from flask import request, render_template
from . import lianlian_pay_entry_mod as mod
from api_x.zyt.evas.lianlian_pay.constant import BizType, NotifyType
from api_x.zyt.evas.lianlian_pay.notify import get_notify_handle
from api_x.zyt.evas.test_pay import NAME
from .commons import parse_and_verify
from .. import is_sending_to_me
from . import notification


@mod.route("/pay/result/<pay_source>", methods=["POST"])
@parse_and_verify
def pay_result(pay_source):
    """支付页面回调, 更多操作可由notify完成，这里只是返回callback"""
    data = request.values
    partner_oid = data['oid_partner']
    order_no = data['no_order']
    pay_result = data['result_pay']
    paybill_oid = data['oid_paybill']

    if not is_sending_to_me(partner_oid):
        return render_template('info.html', title='支付结果', msg='支付异常-订单号:{0}'.format(order_no))

    handle = get_notify_handle(pay_source, BizType.PAY, NotifyType.SYNC)
    if handle:
        # 是否成功，订单号，来源系统，来源系统订单号，数据
        return handle(is_success_result(pay_result), order_no, NAME, paybill_oid, data)

    if is_success_result(pay_result):
        return render_template('info.html', title='支付结果', msg='支付成功(来源未知)-订单号:{0}'.format(order_no))
    return render_template('info.html', title='支付结果', msg='支付失败(来源未知)-订单号:{0}'.format(order_no))


@mod.route("/pay/notify/<pay_source>", methods=["POST"])
@parse_and_verify
def pay_notify(pay_source):
    data = request.values
    partner_oid = data['oid_partner']
    order_no = data['no_order']
    pay_result = data['result_pay']
    paybill_oid = data['oid_paybill']

    if not is_sending_to_me(partner_oid):
        return notification.is_invalid()

    handle = get_notify_handle(pay_source, BizType.PAY, NotifyType.ASYNC)
    if handle:
        # 是否成功，订单号，来源系统，来源系统订单号，数据
        if handle(is_success_result(pay_result), order_no, NAME, paybill_oid, data):
            return notification.succeed()

    return notification.succeed()


def is_success_result(result):
    return result == 'SUCCESS'
