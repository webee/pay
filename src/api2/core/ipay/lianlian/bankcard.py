# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .api import request
from . import config


def query_bin(card_no):
    """ 查询银行卡bin信息
    :param card_no: 银行卡号
    :return:
    """
    params = {
        'oid_partner': config.oid_partner,
        'sign_type': config.sign_type_md5,
        'card_no': card_no
    }
    return request(config.url_query_bankcard_bin, params)
