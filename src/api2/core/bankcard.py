# -*- coding: utf-8 -*-
from .util.attr_dict import AttrDict
from .ipay import transaction
from .ipay.error import UnExpectedResponseError, ApiError
from api2.util.enum import enum
from pytoolbox.util.log import get_logger


_logger = get_logger(__name__)
_bankcard_type = enum(DEBIT='DEBIT', CREDIT='CREDIT')


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
    except ApiError as e:
        _logger.error('card_no: {0}, {1}'.format(card_no, e.message))
        return None


def _parse_card_type(card_type):
    if card_type == 2:
        return _bankcard_type.DEBIT
    elif card_type == 3:
        return _bankcard_type.CREDIT
    raise ValueError("Invalid bank card type [{0}].".format(card_type))
