# coding=utf-8
from __future__ import unicode_literals

from .error import RequestAPIError
from api_x.constant import BankcardType


def query_bin(card_no):
    from api_x.zyt.evas.lianlian_pay import query_bin as _query_bin

    try:
        res = _query_bin(card_no)
    except Exception as e:
        raise RequestAPIError(e.message)

    bank_code = res['bank_code']
    bank_name = res['bank_name']
    card_type = _parse_card_type(res['card_type'])
    return BankcardBin(card_no, bank_code, bank_name, card_type)


class BankcardBin(object):
    def __init__(self, card_no, bank_code, bank_name, card_type):
        self.card_no = card_no
        self.bank_code = bank_code
        self.bank_name = bank_name
        self.card_type = card_type

    def to_dict(self):
        return {
            'card_no': self.card_no,
            'bank_code': self.bank_code,
            'bank_name': self.bank_name,
            'card_type': self.card_type
        }


def _parse_card_type(card_type):
    if card_type == '2':
        return BankcardType.DEBIT
    elif card_type == '3':
        return BankcardType.CREDIT
    raise ValueError("Invalid bank card type [{0}].".format(card_type))
