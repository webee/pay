# coding=utf-8
from __future__ import unicode_literals

from api_x.zyt.biz.payment import get_payment_by_tx_id
from flask import render_template
from api_x.zyt.biz.models import TransactionType
from api_x.utils import req
from ..evas import test_pay, lianlian_pay


def pay(vas_name, tx):
    payment_record = get_payment_by_tx_id(tx.id)
    if vas_name == test_pay.NAME:
        return _pay_by_test_pay(payment_record)
    elif vas_name == lianlian_pay.NAME:
        return _pay_by_lianlian_pay(payment_record)
    return render_template('info.html', title='错误', msg='暂不支持此支付方式')


def _pay_by_test_pay(payment_record):
    from api_x.zyt.evas.test_pay import pay
    return pay(TransactionType.PAYMENT,
               payment_record.payer_id, payment_record.sn, payment_record.product_name, payment_record.amount)


def _pay_by_lianlian_pay(payment_record):
    from api_x.zyt.evas.lianlian_pay import pay
    from api_x.zyt.vas.user import get_user_by_id

    payer = get_user_by_id(payment_record.payer_id)
    return pay(TransactionType.PAYMENT, payer.id, payer.created_on, req.ip(),
               payment_record.sn, payment_record.product_name, payment_record.product_desc, payment_record.amount)
