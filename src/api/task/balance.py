# coding=utf-8
from tools.dbe import require_db_context, require_transaction_context
from tools.lock import require_user_lock
from datetime import datetime
from tools.mylog import get_logger
from api.constant import BookkeepingSide
from api.account.account import get_unsettled_balance

logger = get_logger(__name__)


def update_user_account_balance(account_id, account):
    with require_db_context() as db:
        max_transaction_log_id = db.get_scalar("""
                        select max(id) from %s_account_transaction_log
                        where account_id=%(account_id)s""" % account, account_id=account_id)

    if max_transaction_log_id is None:
        logger.warn("{0} on {1} has no transaction log.".format(account_id, account))
        return

    with require_user_lock(account_id, 'cash_balance'):
        _update_user_account_side_balance(account_id, account, BookkeepingSide.DEBIT, max_transaction_log_id)
        _update_user_account_side_balance(account_id, account, BookkeepingSide.CREDIT, max_transaction_log_id)
        _update_user_account_side_balance(account_id, account, BookkeepingSide.BOTH, max_transaction_log_id)


def _update_user_account_side_balance(account_id, account, side, max_transaction_log_id):
    with require_db_context() as db:
        balance = db.get("""
                      select balance, last_transaction_log_id from account_balance
                      where account_id=%(account_id)s and account=%(account)s and side=%(side)s
                      """, account_id=account_id, account=account, side=side)

        balance_value = 0
        last_transaction_log_id = 0
        if balance:
            balance_value = balance.balance
            last_transaction_log_id = balance.last_transaction_log_id

        unsettled_balance = get_unsettled_balance(db, account_id, side, last_transaction_log_id, max_transaction_log_id)

        new_balance = balance_value + unsettled_balance
        now = datetime.now()
        rowcount = db.execute("""
                    update account_balance set balance=%(balance)s,
                    last_transaction_log_id=%(transaction_id)s, settle_time=%(settle_time)s
                    where account_id=%(account_id)s and side=%(side)s
                    and balance=%(old_balance)s and last_transaction_log_id=%(old_transaction_id)s""",
                              balance=new_balance, transaction_id=max_transaction_log_id, settle_time=now,
                              account_id=account_id, side=side, old_balance=balance_value,
                              old_transaction_id=last_transaction_log_id)
        return rowcount > 0
