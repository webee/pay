# -*- coding: utf-8 -*-
from .util.attr_dict import AttrDict
from ._dba import query_all_bankcards, create_bankcard
from .ipay import transaction
from .ipay.error import UnExpectedResponseError, TransactionApiError
from api2.core import ZytCoreError
from api2.util.enum import enum
from pytoolbox.util.log import get_logger


_logger = get_logger(__name__)
_BANKCARD_TYPE = enum(DEBIT='DEBIT', CREDIT='CREDIT')


class InvalidCardNoError(ZytCoreError):
    def __init__(self, card_no):
        super(InvalidCardNoError, self).__init__("Invalid card number [card_no={0}].".format(card_no))


class TryToBindCreditCardToPrivateAccountError(ZytCoreError):
    def __init__(self, card_no):
        message = "The bank card must be a Debit Card if it was added as private account [card_no={0}].".format(
            card_no)
        super(TryToBindCreditCardToPrivateAccountError, self).__init__(message)


def query_bankcard_bin(card_no):
    try:
        data = transaction.query_bankcard_bin(card_no)
        return AttrDict(
            bank_code=data['bank_code'],
            bank_name=data['bank_name'],
            card_type=_parse_card_type(int(data['card_type']))
        )
    except UnExpectedResponseError as e:
        _logger.error('card_no: {0}, {1}'.format(card_no, e.message))
        return None
    except TransactionApiError as e:
        _logger.error('card_no: {0}, {1}'.format(card_no, e.message))
        return None


def list_all_bankcards(account_id):
    return query_all_bankcards(account_id)


def add_bankcard(account_id, card_no, account_name, is_corporate_account, province_code, city_code, branch_bank_name):
    card = BankCard.load_base_info(card_no)
    if not card:
        raise InvalidCardNoError(card_no)

    card.set_details(account_name, is_corporate_account, province_code, city_code, branch_bank_name)
    if card.is_not_using_debit_card_as_private_account:
        raise TryToBindCreditCardToPrivateAccountError(card_no)

    bankcard_id = create_bankcard(account_id, card)
    return bankcard_id


def _parse_card_type(card_type):
    if card_type == 2:
        return _BANKCARD_TYPE.DEBIT
    elif card_type == 3:
        return _BANKCARD_TYPE.CREDIT
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
        return self.card_type is not None and self.card_type == _BANKCARD_TYPE.DEBIT