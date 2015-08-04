# coding=utf-8
from pytoolbox.util import dbe


@dbe.db_context
def get_account_events(db, account_id):
    return db.list("""
        SELECT e.* FROM
                    (SELECT MAX(id) AS id FROM event WHERE account_id=%(account_id)s GROUP by source_type, source_id)s
                LEFT JOIN event e ON s.id = e.id
                ORDER BY id DESC;
    """, account_id=account_id)
