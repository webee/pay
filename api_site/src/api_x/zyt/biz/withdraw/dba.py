# coding=utf-8
from __future__ import unicode_literals

from api_x.zyt.biz.models import WithdrawRecord
from api_x.zyt.biz.transaction.dba import get_tx_by_sn


def get_withdraw_by_sn(sn):
    return WithdrawRecord.query.filter_by(sn=sn).first()


def get_tx_withdraw_by_sn(sn):
    tx = get_tx_by_sn(sn)
    return tx, tx.record
