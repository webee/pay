# coding=utf-8
from __future__ import unicode_literals

from api_x.zyt.biz.payment import get_payment_by_tx_id
from flask import render_template
from api_x.zyt.biz.models import TransactionType
from api_x.utils import req
from api_x.config import etc as config
from ..evas import test_pay, lianlian_pay
from .. import vas


def pay(vas_name, tx):
    payment_record = get_payment_by_tx_id(tx.id)
    # TODO: 注册支付方式
    if vas_name == test_pay.NAME:
        return _pay_by_test_pay(tx, payment_record)
    elif vas_name == lianlian_pay.NAME:
        return _pay_by_lianlian_pay(tx, payment_record)
    elif vas_name == vas.NAME:
        return _pay_by_zyt_pay(tx)
    return render_template('info.html', title='错误', msg='暂不支持此支付方式')


def _pay_by_test_pay(tx, payment_record):
    from api_x.zyt.evas.test_pay import pay
    return pay(TransactionType.PAYMENT,
               payment_record.payer_id, tx.sn, payment_record.product_name, payment_record.amount)


def _pay_by_lianlian_pay(tx, payment_record):
    from api_x.zyt.evas.lianlian_pay import pay
    from api_x.zyt.user_mapping import get_user_map_by_account_user_id

    user_map = get_user_map_by_account_user_id(payment_record.payer_id)
    user_id = '%s%s.%d' % (config.Biz.TX_SN_PREFIX, user_map.user_id, user_map.user_domain_id)
    return pay(TransactionType.PAYMENT, user_id, user_map.created_on, req.ip(),
               tx.sn, tx.created_on, payment_record.product_name, payment_record.product_desc, payment_record.amount)


def _pay_by_zyt_pay(tx):
    from api_x.zyt.vas import pay
    return pay(TransactionType.PAYMENT, tx.sn)
