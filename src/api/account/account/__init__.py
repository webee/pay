# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from api.account.account import dba
from tools.dbe import require_db_context, db_context
from api.constant import BookkeepingSide


def find_or_create_account(client_id, user_id):
    account_id = find_account_id(client_id, user_id)
    if not account_id:
        fields = {
            'client_id': client_id,
            'user_id': user_id
        }
        with require_db_context() as db:
            account_id = db.insert('account', returns_id=True, **fields)
    return account_id


def find_account_id(client_id, user_id):
    with require_db_context() as db:
        return db.get_scalar(
            """
              SELECT id FROM account
                WHERE client_id = %(client_id)s AND user_id = %(user_id)s
            """, client_id=client_id, user_id=user_id)


@db_context
def get_cash_balance(db, account_id):
    balance_value, last_id = dba.get_settled_balance_and_last_id(db, account_id, 'cash', 'both')
    unsettled_balance = dba.get_unsettled_balance(db, account_id, 'cash', BookkeepingSide.BOTH, last_id)

    return balance_value + unsettled_balance
