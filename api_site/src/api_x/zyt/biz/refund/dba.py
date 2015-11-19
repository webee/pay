# coding=utf-8
from __future__ import unicode_literals
from api_x import db

from api_x.constant import TransactionType, RefundTxState
from api_x.zyt.biz.models import RefundRecord, Transaction
from api_x.zyt.biz.pay.dba import get_payment_by_id
from pytoolbox.util.dbs import transactional


def get_refund_by_tx_id(tx_id):
    return RefundRecord.query.filter_by(tx_id=tx_id).first()


def get_refund_by_sn(sn):
    return RefundRecord.query.filter_by(sn=sn).first()


def get_refund_by_id(id):
    return RefundRecord.query.get(id)


def get_blocked_refunds():
    return Transaction.query.filter_by(type=TransactionType.REFUND, state=RefundTxState.BLOCK).all()


@transactional
def update_payment_refunded_amount(payment_id, refund_amount):
    payment_record = get_payment_by_id(payment_id)

    payment_record.refunded_amount += refund_amount

    db.session.add(payment_record)
