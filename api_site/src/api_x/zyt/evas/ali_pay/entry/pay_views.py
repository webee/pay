# coding=utf-8
from __future__ import unicode_literals

from api_x.zyt.evas.ali_pay.commons import is_success_status
from flask import request, render_template
from . import ali_pay_entry_mod as mod
from api_x.config import ali_pay
from api_x.zyt.evas.ali_pay.constant import NotifyType
from api_x.zyt.evas.ali_pay.notify import get_pay_notify_handle
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
    from ..notify import notify_pay
    data = request.verified_data

    resp_type = notify_pay(source, data)

    return notify_response(resp_type)

