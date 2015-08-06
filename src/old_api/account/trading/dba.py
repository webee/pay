# coding=utf-8
from pytoolbox.util import dbe


@dbe.db_context
def get_cash_events(db, account_id):
    return db.list("""
        SELECT * FROM cash_account_transaction_log c LEFT JOIN event e ON c.event_id=e.id
          WHERE c.account_id=%(account_id)s
          ORDER BY c.id DESC
    """, account_id=account_id)