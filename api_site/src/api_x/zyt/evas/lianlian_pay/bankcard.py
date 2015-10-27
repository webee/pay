# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .api_access import request
from api_x.config import lianlian_pay
from pytoolbox.util.sign import SignType
from .commons import get_pure_result


def user_bankcard(user_id, platform=None):
    """ 查询用户签约信息
    :param user_id 用户id
    :return:
    """
    platform = platform or lianlian_pay.PLATFORM
    params = {
        'oid_partner': lianlian_pay.OID_PARTNER,
        'sign_type': SignType.RSA,
        'platform': platform,
        'user_id': user_id,
        'offset': 0,
    }
    res = request(lianlian_pay.Bankcard.USER_BANKCARD_URL, params)
    return get_pure_result(res)


def unbind_user_bankcard(user_id, no_agree, platform=None):
    """ 解约用户银行卡
    :param user_id 用户id
    :return:
    """
    platform = platform or lianlian_pay.PLATFORM
    params = {
        'oid_partner': lianlian_pay.OID_PARTNER,
        'sign_type': SignType.RSA,
        'platform': platform,
        'user_id': user_id,
        'pay_type': '',
        'no_agree': no_agree
    }
    res = request(lianlian_pay.Bankcard.UNBIND_USER_BANKCARD_URL, params)
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
