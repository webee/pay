# -*- coding: utf-8 -*-
from datetime import datetime

from api.bankcard.bankcard_bin import query_bankcard_bin
from api.util.attr_dict import AttrDict
from api.util.enum import enum
from tools.dbi import from_db, transactional


BankAccount = enum(IsPrivateAccount=0, IsCorporateAccount=1)


class BankCard(object):
    def __init__(self, card_no, bank_code, bank_name, card_type):
        self.no = card_no
        self.bank_code = bank_code
        self.bank_name = bank_name
        self.card_type = card_type
        self.account_name = None
        self.is_corporate_account = False
        self.province_code = None
        self.city_code = None
        self.branch_bank_name = None

    @staticmethod
    def query(card_no):
        bin = query_bankcard_bin(card_no)
        return BankCard(card_no, bin.bank_code, bin.bank_name, bin.card_type) if bin else None

    def set_details(self, account_name, is_corporate_account, province_code, city_code, branch_bank_name):
        self.account_name = account_name
        self.is_corporate_account = is_corporate_account
        self.province_code = province_code
        self.city_code = city_code
        self.branch_bank_name = branch_bank_name

    @property
    def is_not_using_debit_card_as_private_account(self):
        return self._is_private_account() and not self._is_debit_account()

    def _is_private_account(self):
        return not self.is_corporate_account

    def _is_debit_account(self):
        return self.card_type is not None and self.card_type.lower() == 'debit card'


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
        'bank_name': bankcard.bank_name,
        'branch_bank_name': bankcard.branch_bank_name,
        'created_on': datetime.now()
    }
    return from_db().insert('bankcard', returns_id=True, **fields)


def query_bankcard(card_no):
    bin = query_bankcard_bin(card_no)
    BankCard(card_no=card_no, bank_code=bin.bank_code, card_type=bin.card_type)


def is_debit_card(card_no):
    bin = query_bankcard_bin(card_no)
    return bin.card_type == 'Debit Card'


def _gen_bankcard_from_dict(bankcard):
    return AttrDict(**bankcard)
