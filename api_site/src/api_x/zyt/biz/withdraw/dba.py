# coding=utf-8
from __future__ import unicode_literals
from api_x import db
from api_x.dbs import transactional

from api_x.zyt.biz.models import WithdrawRecord
from api_x.zyt.biz.transaction import get_tx_by_sn


def get_withdraw_by_sn(sn):
    return WithdrawRecord.query.filter_by(sn=sn).first()


def get_tx_withdraw_by_sn(sn):
    return get_tx_by_sn(sn), get_withdraw_by_sn(sn)