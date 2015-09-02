# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.evas.lianlian_pay.commons import is_sending_to_me

from flask import request, render_template
from . import lianlian_pay_entry_mod as mod
from api_x.zyt.evas.lianlian_pay.constant import NotifyType
from api_x.zyt.evas.lianlian_pay.notify import get_pay_notify_handle
from api_x.zyt.evas.lianlian_pay import NAME
from .commons import parse_and_verify
from . import notify_response
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


@mod.route("/pay/result/<source>/<order_no>", methods=["POST", "GET"])
@parse_and_verify
def pay_result(source, order_no):
    """支付页面回调, 更多操作可由notify完成，这里只是返回callback"""
    if request.method == "POST":
        data = request.verified_data
        partner_oid = data['oid_partner']
        order_no = data['no_order']
        result = data['result_pay']
        paybill_oid = data['oid_paybill']
        # 这里一定是成功的

        if not is_sending_to_me(partner_oid):
            return render_template('info.html', title='支付结果', msg='支付异常-订单号:{0}'.format(order_no))

        is_success = is_success_result(result)
    elif request.method == "GET":
        is_success = False
        paybill_oid = ""
        data = None

    handle = get_pay_notify_handle(source, NotifyType.Pay.SYNC)
    if handle:
        # 是否成功，订单号，来源系统，来源系统订单号，数据
        return handle(is_success, order_no, NAME, paybill_oid, data)

    if is_success:
        return render_template('info.html', title='支付结果', msg='支付成功({0})-订单号:{1}'.format(source, order_no))
    return render_template('info.html', title='支付结果', msg='支付失败({0})-订单号:{1}'.format(source, order_no))


@mod.route("/pay/notify/<source>", methods=["POST"])
@parse_and_verify
def pay_notify(source):
    data = request.verified_data
    partner_oid = data['oid_partner']
    order_no = data['no_order']
    result = data['result_pay']
    paybill_oid = data['oid_paybill']

    logger.info('pay notify {0}: {1}'.format(source, data))
    if not is_sending_to_me(partner_oid):
        return notify_response.is_invalid()

    handle = get_pay_notify_handle(source, NotifyType.Pay.ASYNC)
    if handle is None:
        return notify_response.miss()

    try:
        # 此通知的调用协议
        # 是否成功，订单号，来源系统，来源系统订单号，数据
        # TODO: 提出接口
        handle(is_success_result(result), order_no, NAME, paybill_oid, data)
        return notify_response.succeed()
    except Exception as e:
        logger.exception(e)
        logger.warning('pay notify error: {0}'.format(e.message))
        return notify_response.failed()


def is_success_result(result):
    return result == 'SUCCESS'
