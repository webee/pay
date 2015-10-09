# coding=utf-8
from __future__ import unicode_literals
from api_x import db

from api_x.zyt.biz.models import RefundRecord
from api_x.zyt.biz.payment.dba import get_payment_by_id
from api_x.zyt.biz.transaction.dba import get_tx_by_sn
from pytoolbox.util.dbs import transactional


def get_refund_by_tx_id(tx_id):
    return RefundRecord.query.filter_by(tx_id=tx_id).first()


def get_refund_by_sn(sn):
    return RefundRecord.query.filter_by(sn=sn).first()


def get_refund_by_id(id):
    return RefundRecord.query.get(id)


def get_tx_refund_by_sn(sn):
    tx = get_tx_by_sn(sn)
    return tx, tx.record


@transactional
def update_payment_refunded_amount(payment_id, refund_amount):
    payment_record = get_payment_by_id(payment_id)

    payment_record.refunded_amount += refund_amount

    db.session.add(payment_record)
