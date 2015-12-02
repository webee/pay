# coding=utf-8
from __future__ import unicode_literals
from decimal import Decimal

from api_x.zyt.evas.ali_pay.commons import is_success_status
from flask import request, render_template
from . import ali_pay_entry_mod as mod
from api_x.config import ali_pay
from api_x.zyt.evas.ali_pay.constant import NotifyType
from api_x.zyt.evas.ali_pay.notify import get_pay_notify_handle
from api_x.zyt.evas.ali_pay import NAME
from .commons import parse_and_verify
from ..commons import notify_verify
from . import notify_response
from api_x.constant import TransactionType
from pytoolbox.util.log import get_logger


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
    seller_id = data['seller_id']

    if not notify_verify(notify_id):
        return render_template('info.html', title='支付结果', msg='支付异常-交易号:{0}'.format(out_trade_no))

    if seller_id != ali_pay.PID:
        return render_template('info.html', title='支付结果', msg='支付异常-交易号:{0}'.format(out_trade_no))

    is_success = is_success_status(trade_status)

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
    out_trade_no = data['out_trade_no']
    trade_no = data['trade_no']
    trade_status = data['trade_status']
    notify_id = data['notify_id']
    total_fee = Decimal(data['total_fee'])
    seller_id = data['seller_id']

    logger.info('pay notify {0}: {1}'.format(source, data))

    if 'refund_status' in data:
        logger.info('ignore refund notify.')
        return notify_response.succeed()

    if not notify_verify(notify_id):
        return notify_response.bad()

    if seller_id != ali_pay.PID:
        return notify_response.bad()

    handle = get_pay_notify_handle(source, NotifyType.Pay.ASYNC)
    if handle is None:
        return notify_response.miss()

    try:
        if trade_status == ali_pay.TradeStatus.TRADE_SUCCESS:
            # 此通知的调用协议
            # 是否成功，订单号，来源系统，来源系统订单号，数据
            handle(is_success_status(trade_status), out_trade_no, NAME, trade_no, total_fee, data)
        elif trade_status == ali_pay.TradeStatus.TRADE_FINISHED:
            # FIXME: 暂时忽略
            logger.info('pay notify the finish: [{0}]'.format(out_trade_no))
        return notify_response.succeed()
    except Exception as e:
        logger.exception(e)
        logger.warning('pay notify error: {0}'.format(e.message))
        return notify_response.failed()
