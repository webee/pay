# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .api_access import request
from api_x.config import lianlian_pay
from pytoolbox.util.sign import SignType
from .commons import get_pure_result


def user_bankcard(user_id):
    """ 查询用户签约信息
    :param user_id 用户id
    :return:
    """
    params = {
        'oid_partner': lianlian_pay.OID_PARTNER,
        'sign_type': SignType.RSA,
        'platform': lianlian_pay.PLATFORM,
        'user_id': user_id,
        'offset': 0,
    }
    res = request(lianlian_pay.Bankcard.USER_BANKCARD_URL, params)
    return get_pure_result(res)


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
    res = request(lianlian_pay.Bankcard.BIN_QUERY_URL, params)
    return get_pure_result(res)
