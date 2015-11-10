# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import url_for, Response
from .commons import generate_absolute_url
from pytoolbox.util.sign import Signer
from pytoolbox.util.log import get_logger
from ..error import PaymentTypeNotSupportedError
from api_x.config import lianlian_pay as config


logger = get_logger(__name__)


NAME = 'LIANLIAN_PAY'

signer = Signer('key', 'sign')


def payment_param(payment_type, source, user_id, user_created_on, ip, order_no, ordered_on, order_name, order_desc,
                  amount):
    from ._payment import pay_param as _pay_param, wap_pay_param as _wap_pay_param, app_params as _app_params

    return_url = generate_absolute_url(url_for('lianlian_pay_entry.pay_result', order_no=order_no))
    notify_url = generate_absolute_url(url_for('lianlian_pay_entry.pay_notify', source=source))

    if payment_type == config.PaymentType.WEB:
        return _pay_param(user_id, user_created_on, ip, order_no, ordered_on, order_name, order_desc, amount,
                          return_url, notify_url)
    elif payment_type == config.PaymentType.WAP:
        return _wap_pay_param(user_id, user_created_on, ip, order_no, ordered_on, order_name, order_desc, amount,
                              return_url, notify_url, config.AppRequest.WAP)
    elif payment_type == config.PaymentType.APP:
        return _app_params(user_id, user_created_on, ip, order_no, ordered_on, order_name, order_desc, amount,
                           notify_url)
    else:
        raise PaymentTypeNotSupportedError(NAME, payment_type)


def pay(source, user_id, user_created_on, ip, order_no, ordered_on, order_name, order_desc, amount,
        app_request=None, channel=None):
    from ._payment import pay as _pay, wap_pay as _wap_pay, app_params as _app_params

    return_url = generate_absolute_url(url_for('lianlian_pay_entry.pay_result', source=source, order_no=order_no))
    notify_url = generate_absolute_url(url_for('lianlian_pay_entry.pay_notify', source=source))

    if channel in [config.Payment.Channel.APP, config.Payment.Channel.API]:
        # app请求参数
        return _app_params(user_id, user_created_on, ip, order_no, ordered_on, order_name, order_desc, amount,
                           notify_url)

    # web请求post form
    #
    if app_request is None:
        return Response(_pay(user_id, user_created_on, ip, order_no, ordered_on, order_name, order_desc, amount,
                             return_url, notify_url))

    # wap支付
    return Response(_wap_pay(user_id, user_created_on, ip, order_no, ordered_on, order_name, order_desc, amount,
                             return_url, notify_url, app_request=app_request))


def refund(source, refund_no, refunded_on, amount, paybill_id):
    from ._refund import refund as _refund

    notify_url = generate_absolute_url(url_for('lianlian_pay_entry.refund_notify', source=source))
    return _refund(refund_no, refunded_on, amount, paybill_id, notify_url)


def query_refund(refund_no, refunded_on, oid_refundno=''):
    from ._refund import refund_query
    return refund_query(refund_no, refunded_on, oid_refundno)


def pay_to_bankcard(source, no_order, money_order, info_order,
                    flag_card, card_type, card_no, acct_name,
                    bank_code='', province_code='', city_code='', brabank_name='',
                    prcptcd=''):
    from ._pay_to_bankcard import pay_to_bankcard as _pay_to_bankcard

    notify_url = generate_absolute_url(url_for('lianlian_pay_entry.pay_to_bankcard_notify', source=source))
    return _pay_to_bankcard(no_order, money_order, info_order, notify_url,
                            flag_card, card_type, card_no, acct_name,
                            bank_code, province_code, city_code, brabank_name, prcptcd)


def query_bin(card_no):
    from .bankcard import query_bin as _query_bin

    return _query_bin(card_no)


def query_refund_notify(source, refund_no, refunded_on, vas_name):
    """ 通过主动查询订单结果来完成结果通知
    :param source: refund来源
    :param refund_no: 退款订单号
    :param refunded_on: 退款订单时间
    :param vas_name: 支付方式名称
    :return:
    """
    from ._refund import refund_query
    from .notify import notify_refund

    data = refund_query(refund_no, refunded_on)

    return notify_refund(source, data)
