# coding=utf-8
from __future__ import unicode_literals

from api_x.zyt.biz import cheque
from api_x.zyt.biz.models import ChequeType


def draw_cheque(channel, from_id, amount, order_id=None, valid_seconds=1800, cheque_type=ChequeType.INSTANT,
                info='', client_notify_url=''):
    return cheque.draw_cheque(channel, from_id, amount, order_id, valid_seconds, cheque_type, info, client_notify_url)


def cash_cheque(channel, to_id, cash_token):
    return cheque.cash_cheque(channel, to_id, cash_token)


def cancel_cheque(channel, user_id, sn):
    return cheque.cancel_cheque(channel, user_id, sn)


def list_cheque(channel, user_id):
    return cheque.list_cheque(channel, user_id)
