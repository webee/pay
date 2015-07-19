# -*- coding: utf-8 -*-
from tools.dbe import require_db_context, db_operate


def find_or_create_account(client_id, user_id):
    account_id = find_account_id(client_id, user_id)
    if not account_id:
        fields = {
            'client_id': client_id,
            'user_id': user_id
        }
        with require_db_context() as db:
            account_id = db.insert('account', returns_id=True, **fields)
    return account_id


def find_account_id(client_id, user_id):
    with require_db_context() as db:
        return db.get_scalar(
            """
              SELECT id FROM account
                WHERE client_id = %(client_id)s AND user_id = %(user_id)s
            """, client_id=client_id, user_id=user_id)


@db_operate
def get_cash_balance(db, account_id):
    """ 得到用户的现金余额
    :param account_id:
    :return:
    """
    return 100
