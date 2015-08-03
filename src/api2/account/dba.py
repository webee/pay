# -*- coding: utf-8 -*-
from pytoolbox.util.dbe import db_context


@db_context
def get_account(db, client_id, user_id):
    return db.get('SELECT * FROM account WHERE client_id=%(client_id)s AND user_id=%(user_id)s', client_id=client_id, user_id=user_id)


@db_context
def find_or_create_account(db, client_id, user_id):
    account = get_account(db, client_id, user_id)
    if account:
        return account['id']

    fields = {
        'client_id': client_id,
        'user_id': user_id
    }
    account_id = db.insert('account', returns_id=True, **fields)
    return account_id

