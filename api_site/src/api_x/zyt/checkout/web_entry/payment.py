# coding=utf-8
from __future__ import unicode_literals

from flask import render_template
from api_x.utils import req
from api_x.zyt.evas import test_pay, lianlian_pay, weixin_pay
from api_x.zyt import vas
from pytoolbox.util.log import get_logger

logger = get_logger(__name__)


def pay(vas_name, payment_entity, request_client_type):
    # TODO: 注册支付方式
    msg = '暂不支持此支付方式'
    try:
        if vas_name == test_pay.NAME:
            return _pay_by_test_pay(payment_entity, request_client_type)
        elif vas_name == lianlian_pay.NAME:
            return _pay_by_lianlian_pay(payment_entity, request_client_type)
        elif vas_name == weixin_pay.NAME:
            return _pay_by_weixin_pay(payment_entity, request_client_type)
        elif vas_name == vas.NAME:
            return _pay_by_zyt_pay(payment_entity, request_client_type)
    except Exception as e:
        logger.exception(e)
        msg = e.message or "请求异常"
    return render_template('info.html', title='错误', msg=msg)


def _pay_by_test_pay(payment_entity, request_client_type):
    from api_x.zyt.evas.test_pay import pay
    return pay(payment_entity.source, payment_entity.user_id, payment_entity.tx_sn,
               payment_entity.product_name, payment_entity.amount)


def _pay_by_lianlian_pay(payment_entity, request_client_type):
    from api_x.constant import RequestClientType
    from api_x.config import lianlian_pay
    from api_x.zyt.evas.lianlian_pay import pay

    # check request client type
    app_request = None
    if request_client_type == RequestClientType.WAP:
        app_request = lianlian_pay.AppRequest.WAP
    elif request_client_type == RequestClientType.IOS:
        app_request = lianlian_pay.AppRequest.IOS
    elif request_client_type == RequestClientType.ANDROID:
        app_request = lianlian_pay.AppRequest.ANDROID

    return pay(payment_entity.source, payment_entity.user_id, payment_entity.user_created_on, req.ip(),
               payment_entity.tx_sn, payment_entity.tx_created_on, payment_entity.product_name,
               payment_entity.product_desc, payment_entity.amount, app_request=app_request)


def _pay_by_weixin_pay(pe, request_client_type):
    """
    微信扫码支付(NATIVE)
    """
    from api_x.config import weixin_pay
    from api_x.zyt.evas.weixin_pay.payment import prepay
    from api_x.zyt.user_mapping import get_channel_by_name

    channel = get_channel_by_name(pe.channel_name)
    app_config = weixin_pay.AppConfig(channel.wx_main)
    code_url = prepay(pe.source, weixin_pay.TradeType.NATIVE, pe.tx_sn, int(100 * pe.amount),
                      req.ip(), pe.product_name, pe.tx_created_on,
                      detail=pe.product_desc, product_id=pe.tx_sn,
                      app_config=app_config)
    return render_template('weixin_pay.html', code_url=code_url, payment_entity=pe)


def _pay_by_zyt_pay(payment_entity, request_client_type):
    from api_x.zyt.vas import pay
    return pay(payment_entity.source, payment_entity.tx_sn)
