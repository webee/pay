# coding=utf-8
from __future__ import unicode_literals

from api_x.zyt.biz import cheque
from api_x.zyt.biz.models import ChequeType


def draw_cheque(channel, from_id, amount, order_id=None, valid_minutes=30, cheque_type=ChequeType.INSTANT,
                info='', client_notify_url=''):
    return cheque.draw_cheque(channel, from_id, amount, order_id, valid_minutes, cheque_type, info, client_notify_url)


def cash_cheque(channel, to_id, cash_token):
    return cheque.cash_cheque(channel, to_id, cash_token)


def cancel_cheque(channel, user_id, sn):
    return cheque.cancel_cheque(channel, user_id, sn)
