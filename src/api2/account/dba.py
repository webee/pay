# -*- coding: utf-8 -*-
from pytoolbox.util.dbe import db_context


@db_context
def find_account_by_user_info(db, user_domain_id, user_id):
    return db.get('SELECT * FROM account WHERE user_domain_id=%(user_domain_id)s AND user_id=%(user_id)s',
                  user_domain_id=user_domain_id, user_id=user_id)


@db_context
def find_account_by_id(db, id):
    return db.get('SELECT * FROM account WHERE id=%(id)s', id=id)


@db_context
def find_secured_account(db):
    return find_account_by_user_info(db, 1, 1)


@db_context
def find_or_create_account(db, user_domain_id, user_id):
    account = find_account_by_user_info(db, user_domain_id, user_id)
    if account:
        return account['id']

    return _create_account(db, user_domain_id, user_id)


@db_context
def find_user_domain_id_by_channel(db, channel_id):
    return db.get_scalar('SELECT user_domain_id FROM channel WHERE id=%(id)s', id=channel_id)


@db_context
def _create_account(db, user_domain_id, user_id):
    fields = {
        'user_domain_id': user_domain_id,
        'user_id': user_id
    }
    return db.insert('account', returns_id=True, **fields)
