# coding=utf-8
from __future__ import unicode_literals

from api_x.zyt.biz.models import WithdrawRecord


def get_withdraw_by_sn(sn):
    return WithdrawRecord.query.filter_by(sn=sn).first()
