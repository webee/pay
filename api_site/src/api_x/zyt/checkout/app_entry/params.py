# coding=utf-8
from __future__ import unicode_literals

from flask import render_template
from api_x.zyt.biz.models import TransactionType
from api_x.utils import req
from api_x.zyt.evas import test_pay, lianlian_pay
from api_x.zyt import vas


def prepare(vas_name, payment_entity):
    if vas_name == test_pay.NAME:
        return _test_pay_params(payment_entity)
    elif vas_name == lianlian_pay.NAME:
        return _lianlian_pay_params(payment_entity)
    elif vas_name == vas.NAME and payment_entity.source == TransactionType.PAYMENT:
        # 自游通支付只支持支付，不支持充值等方式
        return _pay_by_zyt_pay(payment_entity)
    return render_template('info.html', title='错误', msg='暂不支持此支付方式')


def _test_pay_params(payment_entity):
    from api_x.config import test_pay as config
    from api_x.zyt.evas.test_pay import pay

    return pay(payment_entity.source, payment_entity.user_id, payment_entity.tx_sn,
               payment_entity.product_name, payment_entity.amount, channel=config.Pay.CHANNEL.APP)


def _lianlian_pay_params(payment_entity):
    from api_x.config import lianlian_pay as config
    from api_x.zyt.evas.lianlian_pay import pay

    return pay(payment_entity.source, payment_entity.user_id, payment_entity.user_created_on, req.ip(),
               payment_entity.tx_sn, payment_entity.tx_created_on, payment_entity.product_name,
               payment_entity.product_desc, payment_entity.amount, channel=config.Payment.CHANNEL.APP)


def _pay_by_zyt_pay(payment_entity):
    from api_x.zyt.vas import pay
    return pay(TransactionType.PAYMENT, payment_entity.tx_sn)
