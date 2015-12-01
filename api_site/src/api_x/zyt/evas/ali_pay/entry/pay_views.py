# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.evas.lianlian_pay.commons import is_sending_to_me

from flask import request, render_template
from . import ali_pay_entry_mod as mod
from api_x.config import ali_pay
from api_x.zyt.evas.lianlian_pay.constant import NotifyType
from api_x.zyt.evas.lianlian_pay.notify import get_pay_notify_handle
from api_x.zyt.evas.lianlian_pay import NAME
from .commons import parse_and_verify
from ..commons import notify_verify
from . import notify_response
from api_x.constant import TransactionType
from pytoolbox.util.log import get_logger
from decimal import Decimal


logger = get_logger(__name__)


@mod.route("/pay/result/", methods=["GET"])
@parse_and_verify
def pay_result():
    data = request.verified_data
    is_success = data['is_success']
    if is_success != 'T':
        pass

    out_trade_no = data['out_trade_no']
    trade_status = data['trade_status']
    notify_id = data['notify_id']

    if not notify_verify(notify_id):
        return render_template('info.html', title='支付结果', msg='支付异常-交易号:{0}'.format(out_trade_no))

    is_success = is_success_result(trade_status)

    handle = get_pay_notify_handle(TransactionType.PAYMENT, NotifyType.Pay.SYNC)
    if handle:
        # 是否成功，订单号，_数据
        return handle(is_success, out_trade_no, data)

    if is_success:
        return render_template('info.html', title='支付结果', msg='支付成功-交易号:{1}'.format(out_trade_no))
    return render_template('info.html', title='支付结果', msg='支付失败-交易号:{1}'.format(out_trade_no))


@mod.route("/pay/notify/<source>", methods=["POST"])
@parse_and_verify
def pay_notify(source):
    data = request.verified_data
    partner_oid = data['oid_partner']
    order_no = data['no_order']
    result = data['result_pay']
    paybill_oid = data['oid_paybill']
    money_order = Decimal(data['money_order'])

    logger.info('pay notify {0}: {1}'.format(source, data))
    if not is_sending_to_me(partner_oid):
        return notify_response.bad()

    handle = get_pay_notify_handle(source, NotifyType.Pay.ASYNC)
    if handle is None:
        return notify_response.miss()

    try:
        # 此通知的调用协议
        # 是否成功，订单号，来源系统，来源系统订单号，数据
        # TODO: 提出接口
        handle(is_success_result(result), order_no, NAME, paybill_oid, money_order, data)
        return notify_response.succeed()
    except Exception as e:
        logger.exception(e)
        logger.warning('pay notify error: {0}'.format(e.message))
        return notify_response.failed()


def is_success_result(status):
    return status in {ali_pay.TradeStatus.TRADE_SUCCESS, ali_pay.TradeStatus.TRADE_FINISHED}
