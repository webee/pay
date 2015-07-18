# -*- coding: utf-8 -*-
from tools.dbi import from_db


def find_or_create_account(client_id, user_id):
    account_id = find_account_id(client_id, user_id)
    if not account_id:
        fields = {
            'client_id': client_id,
            'user_id': user_id
        }
        account_id = from_db().insert('account', returns_id=True, **fields)
    return account_id


def find_account_id(client_id, user_id):
    return from_db().get_scalar(
        """
          SELECT id FROM account
            WHERE client_id = %(client_id)s AND user_id = %(user_id)s
        """, client_id=client_id, user_id=user_id)


def get_cash_balance(account_id):
    """ 得到用户的现金余额
    :param account_id:
    :return:
    """
    db = from_db()
    return 100
