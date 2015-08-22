# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .api_access import request
from api_x.config import lianlian_pay
from pytoolbox.util.sign import SignType


def query_bin(card_no):
    """ 查询银行卡bin信息
    :param card_no: 银行卡号
    :return:
    """
    params = {
        'oid_partner': lianlian_pay.OID_PARTNER,
        'sign_type': SignType.MD5,
        'card_no': card_no
    }
    return request(lianlian_pay.Bankcard.BIN_QUERY_URL, params)
