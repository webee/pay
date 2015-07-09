# coding=utf-8
from __future__ import unicode_literals


def gen_key_value():
    """生成随机64位key value.
    :return: key value.
    """
    import os
    return os.urandom(32).encode('hex')


def gen_transaction_id(user_db_id):
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d%H%M%S%f") + '%0.7d' % user_db_id


def get_or_create_account(user_source, user_id):
    if user_source and user_id:
        from tools.dbi import from_db, require_transaction_context

        db = from_db()

        account = db.get("select * from account where user_source=%(user_source)s and user_id=%(user_id)s",
                         user_source=user_source, user_id=user_id)

        if account is None:
            with require_transaction_context():
                db_id = db.insert('account', user_source=user_source, user_id=user_id)

            account = db.get("select * from account where user_source=%(user_source)s and user_id=%(user_id)s",
                             user_source=user_source, user_id=user_id)

        return account
    # 匿名用户
    return {"id": 0}
