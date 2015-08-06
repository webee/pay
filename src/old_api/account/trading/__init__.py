# coding=utf-8
from . import dba


def query_trading_records(account_id):
    events = dba.get_account_events(account_id)
    pass
