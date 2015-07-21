# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
from tools.dbe import require_db_context, db_operate
from api.constant import BookkeepingSide


def user_account_exists(account_id):
    with require_db_context() as db:
        return db.exists("select 1 from account where id=%(account_id)s", account_id=account_id)


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


@db_operate
def get_cash_balance(db, account_id):
    balance = db.get("""
          select balance, last_transaction_log_id from account_balance
          where account_id=%(account_id)s and account='cash' and side='both'
          """, account_id=account_id)
    balance_value = Decimal(0)
    last_transaction_log_id = 0
    if balance:
        balance_value = balance.balance
        last_transaction_log_id = balance.last_transaction_log_id

    unsettled_balance = get_unsettled_balance(db, account_id, 'cash', BookkeepingSide.BOTH, last_transaction_log_id)
    unsettled_balance = Decimal(0) if unsettled_balance is None else unsettled_balance
    return balance_value + unsettled_balance


def get_unsettled_balance(db, account_id, account, side, low_id, high_id=None):
    if side == BookkeepingSide.BOTH:
        if high_id is None:
            return db.get_scalar("""
                      select sum((CASE side WHEN 'debit' THEN -1 WHEN 'credit' THEN 1 END) * amount)
                      from """ + account + """_account_transaction_log
                      where account_id=%(account_id)s and id > %(low_id)s
                      """, account_id=account_id, low_id=low_id)
        else:
            return db.get_scalar("""
                    select sum((CASE side WHEN 'debit' THEN -1 WHEN 'credit' THEN 1 END) * amount)
                    from """ + account + """_account_transaction_log
                    where account_id=%(account_id)s and id > %(low_id)s and id <= %(high_id)s
                    """, account_id=account_id, low_id=low_id, high_id=high_id)
    else:
        if high_id is None:
            return db.get_scalar("""
                      select sum((CASE side WHEN 'debit' THEN -1 WHEN 'credit' THEN 1 END) * amount)
                      from """ + account + """_account_transaction_log
                      where account_id=%(account_id)s and side=%(side)s and id > %(low_id)s
                      """, account_id=account_id, side=side, low_id=low_id)
        else:
            return db.get_scalar("""
                    select sum((CASE side WHEN 'debit' THEN -1 WHEN 'credit' THEN 1 END) * amount)
                    from """ + account + """_account_transaction_log
                    where account_id=%(account_id)s and side=%(side)s and id > %(low_id)s and id <= %(high_id)s
                    """, account_id=account_id, side=side, low_id=low_id, high_id=high_id)
