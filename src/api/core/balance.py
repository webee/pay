# -*- coding: utf-8 -*-
from ._dba import get_settled_balance_and_last_id, BOOKKEEPING_SIDE, get_unsettled_balance


def get_cash_balance(account_id):
    balance_value, last_id = get_settled_balance_and_last_id(account_id, 'cash', BOOKKEEPING_SIDE.BOTH)
    unsettled_balance = get_unsettled_balance(account_id, 'cash', BOOKKEEPING_SIDE.BOTH, last_id)

    return balance_value + unsettled_balance