# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from api.util.attr_dict import AttrDict
from api.util.ipay import transaction
from api.util.ipay.error import UnExpectedResponseError
from api.util.ipay.transaction import ApiError
from api.constant import BankcardType
from tools.mylog import get_logger


logger = get_logger(__name__)


def query_bankcard_bin(card_no):
    try:
        data = transaction.query_bankcard_bin(card_no)
        return AttrDict(
            bank_code=data['bank_code'],
            bank_name=data['bank_name'],
            card_type=_parse_card_type(int(data['card_type']))
        )
    except UnExpectedResponseError as e:
        logger.info('card_no: {0}, {1}'.format(card_no, e.message))
        return None
    except ApiError as e:
        logger.info('card_no: {0}, {1}'.format(card_no, e.message))
        return None


def _parse_card_type(card_type):
    if card_type == 2:
        return BankcardType.DEBIT
    elif card_type == 3:
        return BankcardType.CREDIT
    raise ValueError("Invalid bank card type [{0}].".format(card_type))
