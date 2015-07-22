# coding=utf-8
from __future__ import unicode_literals, print_function

from decimal import Decimal
from tools.dbe import require_transaction_context, db_operate
from tools.lock import require_user_lock, GetLockError, GetLockTimeoutError
from datetime import datetime
from tools.mylog import get_logger
from api.util.bookkeeping import get_account_side_sign
from api.constant import BookkeepingSide

logger = get_logger(__name__)


def settle_user_account_balance(account_id, account, high_id=None):
    high_id = _get_user_account_max_id(account) if high_id is None else high_id

    if high_id is None:
        logger.warn("{0} on {1} has no transaction log.".format(account_id, account))
        return

    try:
        with require_user_lock(account_id, 'cash_balance'):
            with require_transaction_context() as db:
                _settle_user_account_side_balance(db, account_id, account, BookkeepingSide.DEBIT, high_id)
                _settle_user_account_side_balance(db, account_id, account, BookkeepingSide.CREDIT, high_id)
                _settle_user_account_side_balance(db, account_id, account, BookkeepingSide.BOTH, high_id)
    except GetLockError as e:
        logger.warn(e.message)
    except GetLockTimeoutError as e:
        logger.warn(e.message)


@db_operate
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


@db_operate
def _get_user_account_max_id(db, account):
    account_table = account + "_account_transaction_log"
    return db.get_scalar("""SELECT MAX(id) FROM """ + account_table)


def _settle_user_account_side_balance(db, account_id, account, side, high_id):
    balance_value, low_id = get_settled_balance_and_last_id(db, account_id, account, side, True)
    if low_id >= high_id:
        return 0

    unsettled_balance = get_unsettled_balance(db, account_id, account, side, low_id, high_id)
    new_balance = balance_value + unsettled_balance

    now = datetime.now()
    rowcount = db.execute("""
                UPDATE account_balance
                  SET
                    balance=%(balance)s, last_transaction_log_id=%(transaction_id)s, settle_time=%(settle_time)s
                  WHERE
                    account_id=%(account_id)s AND account=%(account)s AND side=%(side)s
                      AND balance=%(old_balance)s AND last_transaction_log_id=%(old_transaction_id)s""",
                          balance=new_balance, transaction_id=high_id, settle_time=now,
                          account_id=account_id, account=account, side=side, old_balance=balance_value,
                          old_transaction_id=low_id)
    return rowcount


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


def get_unsettled_balance(db, account_id, account, side, low_id, high_id=None):
    debit_sign, credit_sign = get_account_side_sign(account)
    account_table = account + "_account_transaction_log"
    if side == BookkeepingSide.BOTH:
        if high_id is None:
            balance = db.get_scalar("""
              SELECT SUM((CASE side WHEN 'debit' THEN %(debit_sign)s WHEN 'credit' THEN %(credit_sign)s END) * amount)
                FROM """ + account_table + """
                WHERE
                  account_id=%(account_id)s and id > %(low_id)s
              """, debit_sign=debit_sign, credit_sign=credit_sign, account_id=account_id, low_id=low_id)
        else:
            balance = db.get_scalar("""
            SELECT SUM((CASE side WHEN 'debit' THEN %(debit_sign)s WHEN 'credit' THEN %(credit_sign)s END) * amount)
              FROM """ + account_table + """
              WHERE
                account_id=%(account_id)s and id > %(low_id)s and id <= %(high_id)s
            """, debit_sign=debit_sign, credit_sign=credit_sign, account_id=account_id, low_id=low_id, high_id=high_id)
    else:
        if high_id is None:
            balance = db.get_scalar("""
                      SELECT SUM(amount)
                        FROM """ + account_table + """
                        WHERE
                          account_id=%(account_id)s and side=%(side)s and id > %(low_id)s
                      """, account_id=account_id, side=side, low_id=low_id)
        else:
            balance = db.get_scalar("""
                    SELECT SUM(amount)
                      FROM """ + account_table + """
                      WHERE
                        account_id=%(account_id)s and side=%(side)s and id > %(low_id)s and id <= %(high_id)s
                    """, account_id=account_id, side=side, low_id=low_id, high_id=high_id)

    return Decimal(0) if balance is None else balance
