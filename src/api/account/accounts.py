# coding=utf-8
from tools.dbi import from_db


def cash_account_balance(account_id):
    """ 得到用户的现金余额
    :param account_id:
    :return:
    """
    db = from_db()
    return 100
