# -*- coding: utf-8 -*-
from pytoolbox.util.dbe import db_context


@db_context
def get_cash_balance(db, account_id):
    balance_value, last_id = get_settled_balance_and_last_id(db, account_id, 'cash', 'both')
    unsettled_balance = get_unsettled_balance(db, account_id, 'cash', BookkeepingSide.BOTH, last_id)

    return balance_value + unsettled_balance
