# coding=utf-8
from __future__ import unicode_literals

from decimal import Decimal
from . import dba
import api_x.utils.times
from .models import WithdrawState


def apply_to_withdraw(channel, order_id, from_user_id, bankcard, amount, fee, client_notify_url, data):
    # FIXME:
    # 在application成为真正独立子系统时，这里应该使用api交互
    from api_x.zyt.biz import withdraw
    withdraw_record = withdraw.apply_to_withdraw(channel, order_id, from_user_id, bankcard.flag, bankcard.card_type,
                                                 bankcard.card_no,
                                                 bankcard.acct_name, bankcard.bank_code, bankcard.province_code,
                                                 bankcard.city_code, bankcard.bank_name, bankcard.brabank_name,
                                                 bankcard.prcptcd,
                                                 amount, fee, client_notify_url, data)

    return withdraw_record


def log_user_withdraw(user_id, tx_sn, bankcard_id, amount, actual_amount, fee):
    dba.add_user_withdraw_log(user_id, tx_sn, bankcard_id, amount, actual_amount, fee, WithdrawState.PROCESSING)


def calc_user_withdraw_fee(user_id, amount):
    """手续费策略"""
    withdraw_logs = dba.query_user_withdraw_logs(user_id, api_x.utils.times.utctoday())

    if len(withdraw_logs) > 0:
        return Decimal('2.00')
    return Decimal('0.00')