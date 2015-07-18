# -*- coding: utf-8 -*-
from api.util.attr_dict import AttrDict
from api.util.ipay import transaction
from api.util.ipay.error import UnExpectedResponseError


def query_bankcard_bin(card_no):
    try:
        data = transaction.query_bankcard_bin(card_no)
        return AttrDict(
            bank_code=data['bank_code'],
            bank_name=data['bank_name'],
            card_type=_parse_card_type(int(data['card_type']))
        )
    except UnExpectedResponseError:
        return None


def _parse_card_type(card_type):
    if card_type == 2:
        return 'Debit Card'
    elif card_type == 3:
        return 'Credit Card'
    raise ValueError("Invalid bank card type [{0}].".format(card_type))