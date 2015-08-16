# -*- coding: utf-8 -*-
from entry.util.attr_dict import AttrDict
from entry.constant import BankcardType, BankAccount
from .api.zyt.biz.models import Bankcard
from entry.utils import transactional
from entry import db


def query_bankcard_bin(card_no):
    from entry.core.es.lianlian.bankcard import query_bin
    try:
        data = query_bin(card_no)
        return AttrDict(
            bank_code=data['bank_code'],
            bank_name=data['bank_name'],
            card_type=_parse_card_type(int(data['card_type']))
        )
    except Exception:
        return None


def list_all_bankcards(user_id):
    return Bankcard.query.filter_by(user_id=user_id).all()


class InvalidCardNoError(Exception):
    def __init__(self, card_no):
        msg = 'invalid card no: {0}'.format(card_no)
        super(InvalidCardNoError, self).__init__(msg)


class TryToBindCreditCardToPrivateAccountError(Exception):
    def __init__(self, card_no):
        msg = 'card no: {0}'.format(card_no)
        super(InvalidCardNoError, self).__init__(msg)


@transactional
def create_bankcard(user_id, card):
    bankcard = Bankcard(user_id=user_id, card_no=card.no, card_type=card.card_type, account_name=card.account_name,
                        flag=BankAccount.IS_CORPORATE_ACCOUNT if card.is_corporate_account else BankAccount.IS_PRIVATE_ACCOUNT,
                        bank_code=card.bank_code, province_code=card.province_code, city_code=card.city_code,
                        bank_name=card.bank_name, branch_bank_name=card.branch_bank_name)

    db.session.add(bankcard)

    return bankcard


def query_bankcard(user_id, bankcard_id):
    return Bankcard.query.filter_by(user_id=user_id, id=bankcard_id).first()


def add_bankcard(user_id, card_no, account_name, is_corporate_account, province_code, city_code, branch_bank_name):
    card = BankCard.load_base_info(card_no)
    if not card:
        raise InvalidCardNoError(card_no)

    card.set_details(account_name, is_corporate_account, province_code, city_code, branch_bank_name)
    if card.is_not_using_debit_card_as_private_account:
        raise TryToBindCreditCardToPrivateAccountError(card_no)

    bankcard = create_bankcard(user_id, card)
    return bankcard.id


def _parse_card_type(card_type):
    if card_type == 2:
        return BankcardType.DEBIT
    elif card_type == 3:
        return BankcardType.CREDIT
    raise ValueError("Invalid bank card type [{0}].".format(card_type))


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
    def load_base_info(card_no):
        bankcard_bin = query_bankcard_bin(card_no)
        return BankCard(card_no, bankcard_bin.bank_code,
                        bankcard_bin.bank_name, bankcard_bin.card_type) if bankcard_bin else None

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
        return self.card_type is not None and self.card_type == BankcardType.DEBIT