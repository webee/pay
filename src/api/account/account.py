# -*- coding: utf-8 -*-
from tools.dbe import require_db_context, db_operate
from tools.lock import require_user_locker


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
    with require_user_locker(account_id, "cash_balance"):
        balance = db.get("""
              select balance, last_transaction_log_id from account_balance
              where account_id=%(account_id)s and account='cash' and side='both'
              """, account_id=account_id)
        balance_value = 0
        last_transaction_log_id = 0
        if balance:
            balance_value = balance.balance
            last_transaction_log_id = balance.last_transaction_log_id

        unsettled_balance = db.get_scalar("""
                select sum((CASE side WHEN 'debit' THEN -1 WHEN 'credit' THEN 1 END) * amount) from cash_account_transaction_log
                where account_id=%(account_id)s and id > %(id)s
                """, account_id=account_id, id=last_transaction_log_id)
        return balance_value + unsettled_balance
