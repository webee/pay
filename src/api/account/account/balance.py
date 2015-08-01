# coding=utf-8
from __future__ import unicode_literals, print_function

from datetime import datetime

from . import dba
from api.account.account.dba import get_user_account_max_id
from pytoolbox.util.dbe import require_transaction_context
from tools.lock import require_user_lock, GetLockError, GetLockTimeoutError
from tools.mylog import get_logger
from api.constant import BookkeepingSide

logger = get_logger(__name__)


def settle_user_account_balance(account_id, account, high_id=None):
    high_id = get_user_account_max_id(account) if high_id is None else high_id

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


def _settle_user_account_side_balance(db, account_id, account, side, high_id):
    balance_value, low_id = dba.get_settled_balance_and_last_id(db, account_id, account, side, True)
    if low_id >= high_id:
        return 0

    unsettled_balance = dba.get_unsettled_balance(db, account_id, account, side, low_id, high_id)
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
