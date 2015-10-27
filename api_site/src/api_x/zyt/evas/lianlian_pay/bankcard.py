# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .api_access import request
from api_x.config import lianlian_pay
from pytoolbox.util.sign import SignType
from pytoolbox.util.log import get_logger
from .commons import get_pure_result


logger = get_logger(__name__)


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


def unbind_user_bankcards(user_id, platform=None):
    """ 解约用户所有的银行卡
    :param user_id 用户id
    :return:
    """
    platform = platform or lianlian_pay.PLATFORM
    try:
        data = user_bankcard(user_id, platform)
        user_id = data['user_id']
        count = int(data['count'])
        logger.info('user {0} binds {1} bankcards.'.format(user_id, count))
        for bankcard in data['agreement_list']:
            bank_name = bankcard['bank_name']
            bind_mobile = bankcard['bind_mobile']
            card_no = bankcard['card_no']
            no_agree = bankcard['no_agree']
            card_type = {'2': '储蓄卡', '3': '信用卡'}.get(bankcard['card_type'], '其它')
            logger.info('unbind {0}#({1}){2}@{3}.'.format(bind_mobile, card_type, card_no, bank_name))
            try:
                unbind_user_bankcard(user_id, no_agree, platform)
            except Exception as e:
                logger.error(e.message)
    except Exception as e:
        logger.error(e.message)


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
