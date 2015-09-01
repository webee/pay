# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.biz.models import PaymentRecord
from api_x.zyt.biz.transaction.dba import get_tx_by_sn


def get_payment_by_channel_order_id(channel_id, order_id):
    return PaymentRecord.query.filter_by(channel_id=channel_id, order_id=order_id).first()


def get_payment_by_tx_id(tx_id):
    return PaymentRecord.query.filter_by(tx_id=tx_id).first()


def get_payment_by_sn(sn):
    return PaymentRecord.query.filter_by(sn=sn).first()


def get_payment_by_id(id):
    return PaymentRecord.query.get(id)


def get_tx_payment_by_sn(sn):
    return get_tx_by_sn(sn), get_payment_by_sn(sn)