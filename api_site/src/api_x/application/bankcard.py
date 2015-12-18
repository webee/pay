# -*- coding: utf-8 -*-
from .error import *
from api_x.constant import BankcardType
from pytoolbox.util.log import get_logger
from . import dba


logger = get_logger(__name__)


def query_bin(card_no):
    # FIXME:
    # 在application成为真正独立子系统时，这里应该使用api交互
    from api_x.zyt.biz import bankcard

    return bankcard.query_bin(card_no)


def query_bin_cache(card_no):
    # 缓存bankcard_bin信息
    bankcard_bin = dba.get_bankcard_bin(card_no)
    if bankcard_bin is None:
        bankcard_bin = query_bin(card_no)
        dba.add_bankcard_bin(bankcard_bin)
    return bankcard_bin


def bind_bankcard(user_id, card_no, acct_name, is_corporate_account, province_code, city_code, brabank_name):
    bankcard_info = BankCardInfo.load_base_info(card_no)
    if not bankcard_info:
        raise InvalidCardNoError(card_no)

    bankcard_info.set_details(acct_name, is_corporate_account, province_code, city_code, brabank_name)
    if bankcard_info.is_not_using_debit_card_as_private_account:
        raise TryToBindCreditCardToPrivateAccountError(card_no)

    bankcard = dba.bind_bankcard(user_id, bankcard_info)
    return bankcard.id


def unbind_bankcard(user_id, bankcard_id):
    dba.unbind_bankcard(user_id, bankcard_id)


class BankCardInfo(object):
    def __init__(self, card_no, bank_code, bank_name, card_type):
        self.card_no = card_no
        self.bank_code = bank_code
        self.bank_name = bank_name
        self.card_type = card_type
        self.acct_name = None
        # FIXME: 目前都默认是对私账号
        self.is_corporate_account = False
        self.province_code = None
        self.city_code = None
        self.brabank_name = None

    @staticmethod
    def load_base_info(card_no):
        bankcard_bin = query_bin_cache(card_no)
        return BankCardInfo(card_no, bankcard_bin.bank_code,
                            bankcard_bin.bank_name, bankcard_bin.card_type) if bankcard_bin else None

    def set_details(self, acct_name, is_corporate_account, province_code, city_code, brabank_name):
        self.acct_name = acct_name
        self.is_corporate_account = is_corporate_account
        self.province_code = province_code
        self.city_code = city_code
        self.brabank_name = brabank_name

    @property
    def is_not_using_debit_card_as_private_account(self):
        return self._is_private_account() and not self._is_debit_account()

    def _is_private_account(self):
        return not self.is_corporate_account

    def _is_debit_account(self):
        return self.card_type == BankcardType.DEBIT