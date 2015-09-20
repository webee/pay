# coding=utf-8
from __future__ import unicode_literals

from api_x.zyt.user_mapping import get_user_map_by_account_user_id
from flask import render_template
from api_x.zyt.biz.models import TransactionType
from api_x.utils import req
from api_x.config import etc as config
from ..evas import test_pay, lianlian_pay
from .. import vas


def pay(vas_name, payment_entity, request_client_type):
    # TODO: 注册支付方式
    if vas_name == test_pay.NAME:
        return _pay_by_test_pay(payment_entity, request_client_type)
    elif vas_name == lianlian_pay.NAME:
        return _pay_by_lianlian_pay(payment_entity, request_client_type)
    elif vas_name == vas.NAME and payment_entity.source == TransactionType.PAYMENT:
        # 自游通支付只支持支付，不支持充值等方式
        return _pay_by_zyt_pay(payment_entity, request_client_type)
    return render_template('info.html', title='错误', msg='暂不支持此支付方式')


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


def _pay_by_zyt_pay(payment_entity, request_client_type):
    from api_x.zyt.vas import pay
    return pay(TransactionType.PAYMENT, payment_entity.tx_sn)


class PaymentEntity(object):
    def __init__(self, source, user_id, user_created_on, tx_sn, tx_created_on,
                 product_name, product_desc, amount):
        self.source = source
        self.user_id = user_id
        self.user_created_on = user_created_on
        self.tx_sn = tx_sn
        self.tx_created_on = tx_created_on
        self.product_name = product_name
        self.product_desc = product_desc
        self.amount = amount


def gen_payment_entity_by_pay_tx(tx):
    payment_record = tx.record

    user_map = get_user_map_by_account_user_id(payment_record.payer_id)
    user_id = '%s%s.%d' % (config.Biz.TX_SN_PREFIX, user_map.user_id, user_map.user_domain_id)

    return PaymentEntity(TransactionType.PAYMENT, user_id, user_map.created_on, tx.sn, tx.created_on,
                         payment_record.product_name, payment_record.product_desc,
                         payment_record.amount)


def gen_payment_entity_by_prepaid_tx(tx):
    prepaid_record = tx.record

    user_map = get_user_map_by_account_user_id(prepaid_record.to_id)
    user_id = '%s%s.%d' % (config.Biz.TX_SN_PREFIX, user_map.user_id, user_map.user_domain_id)

    return PaymentEntity(TransactionType.PREPAID, user_id, user_map.created_on, tx.sn, tx.created_on,
                         "充值", tx.comments,
                         prepaid_record.amount)
