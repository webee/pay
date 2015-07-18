# -*- coding: utf-8 -*-
from datetime import datetime

from api.util.attr_dict import AttrDict
from api.util.enum import enum
from tools.dbi import from_db, transactional

BankAccount = enum(IsPrivateAccount=0, IsCorporateAccount=1)


class BankCard(object):
    def __init__(self, card_no, account_name, is_corporate_account, bank_code, province_code, city_code,
                 branch_bank_name):
        self.no = card_no
        self.account_name = account_name
        self.is_corporate_account = is_corporate_account
        self.bank_code = bank_code
        self.province_code = province_code
        self.city_code = city_code
        self.branch_bank_name = branch_bank_name


def list_all_bankcards(account_id):
    return from_db().list("SELECT * FROM bankcard WHERE account_id=%(account_id)s", account_id=account_id)


def get_bankcard(account_id, bankcard_id):
    bankcard = from_db().get('SELECT * FROM bankcard WHERE account_id=%(account_id)s AND id=%(bankcard_id)s',
                             account_id=account_id, bankcard_id=bankcard_id)
    if bankcard:
        return _gen_bankcard_from_dict(bankcard)


@transactional
def new_bankcard(account_id, bankcard):
    fields = {
        'account_id': account_id,
        'card_no': bankcard.no,
        'account_name': bankcard.account_name,
        'flag': BankAccount.IsCorporateAccount if bankcard.is_corporate_account else BankAccount.IsPrivateAccount,
        'bank_code': bankcard.bank_code,
        'province_code': bankcard.province_code,
        'city_code': bankcard.city_code,
        'branch_bank_name': bankcard.branch_bank_name,
        'created_on': datetime.now()
    }
    return from_db().insert('bankcard', returns_id=True, **fields)


def _gen_bankcard_from_dict(bankcard):
    return AttrDict(**bankcard)
