# -*- coding: utf-8 -*-
from pytoolbox.util.dbe import db_context


@db_context
def find_account_by_user_info(db, client_id, user_id):
    return db.get('SELECT * FROM account WHERE client_id=%(client_id)s AND user_id=%(user_id)s', client_id=client_id, user_id=user_id)


@db_context
def find_account_by_id(db, id):
    return db.get('SELECT * FROM account WHERE id=%(id)s', id=id)


@db_context
def find_or_create_account(db, client_id, user_id):
    account = find_account_by_user_info(db, client_id, user_id)
    if account:
        return account['id']

    create_account(db, client_id, user_id)


@db_context
def create_account(db, client_id, user_id, desc):
    fields = {
        'client_id': client_id,
        'user_id': user_id,
        'info': desc
    }
    return db.insert('account', returns_id=True, **fields)
