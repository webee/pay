# coding=utf-8
from __future__ import unicode_literals

from decimal import Decimal
from . import dba
from api_x.utils import date_and_time as dat
from .models import WithdrawState


def apply_to_withdraw(channel, from_user_id, bankcard, amount, fee, client_notify_url, data):
    # FIXME:
    # 在application成为真正独立子系统时，这里应该使用api交互
    from api_x.zyt.biz import withdraw
    withdraw_record = withdraw.apply_to_withdraw(channel, from_user_id, bankcard.flag, bankcard.card_type, bankcard.card_no,
                                                 bankcard.acct_name, bankcard.bank_code, bankcard.province_code,
                                                 bankcard.city_code, bankcard.bank_name, bankcard.brabank_name,
                                                 bankcard.prcptcd,
                                                 amount, fee, client_notify_url, data)

    return withdraw_record.sn


def log_user_withdraw(user_id, tx_sn, bankcard_id, amount, fee):
    dba.add_user_withdraw_log(user_id, tx_sn, bankcard_id, amount, fee, WithdrawState.PROCESSING)


def calc_user_withdraw_fee(user_id, amount):
    """手续费策略"""
    withdraw_logs = dba.query_user_withdraw_logs(user_id, dat.utctoday())

    if len(withdraw_logs) > 0:
        return Decimal('2.00')
    return Decimal('0.00')