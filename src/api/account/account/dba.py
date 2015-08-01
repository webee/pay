# coding=utf-8
from datetime import datetime
from decimal import Decimal
from api.constant import BookkeepingSide
from api.util.bookkeeping import get_account_side_sign
from pytoolbox.util.dbe import db_context


@db_context
def user_account_exists(db, account_id):
    return db.exists("select 1 from account where id=%(account_id)s", account_id=account_id)


@db_context
def list_users_with_unsettled_cash(db):
    return db.list("""
            SELECT a.account_id, a.high_id
              FROM
                (SELECT account_id, MAX(id) AS high_id FROM cash_account_transaction_log GROUP BY account_id)a
              LEFT JOIN
                (SELECT account_id, MIN(last_transaction_log_id) AS low_id FROM account_balance GROUP BY account_id)b
              ON a.account_id=b.account_id
                WHERE
                  b.low_id is null or a.high_id > b.low_id""")


@db_context
def get_user_account_max_id(db, account):
    account_table = account + "_account_transaction_log"
    return db.get_scalar("""SELECT MAX(id) FROM """ + account_table)


@db_context
def get_unsettled_balance(db, account_id, account, side, low_id, high_id=None):
    account_table = account + "_account_transaction_log"
    if side == BookkeepingSide.BOTH:
        debit_sign, credit_sign = get_account_side_sign(account)
        if high_id is None:
            balance = db.get_scalar("""
              SELECT SUM((CASE side WHEN 'debit' THEN %(debit_sign)s WHEN 'credit' THEN %(credit_sign)s END) * amount)
                FROM """ + account_table + """
                WHERE account_id=%(account_id)s and id > %(low_id)s
              """, debit_sign=debit_sign, credit_sign=credit_sign, account_id=account_id, low_id=low_id)
        else:
            balance = db.get_scalar("""
            SELECT SUM((CASE side WHEN 'debit' THEN %(debit_sign)s WHEN 'credit' THEN %(credit_sign)s END) * amount)
              FROM """ + account_table + """
              WHERE account_id=%(account_id)s and id > %(low_id)s and id <= %(high_id)s
            """, debit_sign=debit_sign, credit_sign=credit_sign, account_id=account_id, low_id=low_id, high_id=high_id)
    else:
        if high_id is None:
            balance = db.get_scalar("""
                      SELECT SUM(amount)
                        FROM """ + account_table + """
                        WHERE account_id=%(account_id)s and side=%(side)s and id > %(low_id)s
                      """, account_id=account_id, side=side, low_id=low_id)
        else:
            balance = db.get_scalar("""
                    SELECT SUM(amount)
                      FROM """ + account_table + """
                      WHERE account_id=%(account_id)s and side=%(side)s and id > %(low_id)s and id <= %(high_id)s
                    """, account_id=account_id, side=side, low_id=low_id, high_id=high_id)

    return Decimal(0) if balance is None else balance


@db_context
def get_settled_balance_and_last_id(db, account_id, account, side, create=False):
    balance = db.get("""
                  SELECT balance, last_transaction_log_id
                    FROM account_balance
                    WHERE
                      account_id=%(account_id)s and account=%(account)s and side=%(side)s
                  """, account_id=account_id, account=account, side=side)

    balance_value = Decimal(0)
    last_transaction_log_id = 0
    if balance is None and create:
        db.insert("account_balance", account_id=account_id, account=account, side=side,
                  balance=balance_value, last_transaction_log_id=last_transaction_log_id, settle_time=datetime.now())
    elif balance:
        balance_value = balance.balance
        last_transaction_log_id = balance.last_transaction_log_id
    return balance_value, last_transaction_log_id


@db_context
def get_account(db, client_id, user_id):
    return db.get('SELECT * FROM account WHERE client_id=%(client_id)s AND user_id=%(user_id)s', client_id=client_id, user_id=user_id)


@db_context
def get_account_by_id(db, id):
    return db.get('SELECT * FROM account WHERE id=%(id)s', id=id)