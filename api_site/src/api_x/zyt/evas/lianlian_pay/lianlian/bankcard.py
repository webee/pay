# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .api_access import request
from api_x import config


def query_bin(card_no):
    """ 查询银行卡bin信息
    :param card_no: 银行卡号
    :return:
    """
    params = {
        'oid_partner': config.LianLianPay.OID_PARTNER,
        'sign_type': config.LianLianPay.Sign.MD5_TYPE,
        'card_no': card_no
    }
    return request(config.LianLianPay.BankcardBinQuery.URL, params)
