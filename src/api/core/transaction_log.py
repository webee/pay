# coding=utf-8
from . import _dba


def get_user_cash_account_records(account_id):
    return _dba.get_user_cash_account_log(account_id)
