# coding=utf-8
from __future__ import unicode_literals

from flask import render_template
from api_x.zyt import vas
from pytoolbox.util.log import get_logger

logger = get_logger(__name__)


def pay(vas_name, payment_entity, request_client_type):
    # TODO: 注册支付方式
    msg = '暂不支持此支付方式'
    try:
        if vas_name == vas.NAME:
            return _pay_by_zyt_pay(payment_entity, request_client_type)
    except Exception as e:
        logger.exception(e)
        msg = e.message or "请求异常"
    return render_template('info.html', title='错误', msg=msg)


def _pay_by_zyt_pay(payment_entity, request_client_type):
    from api_x.zyt.vas import pay
    return pay(payment_entity.source, payment_entity.tx_sn)
