# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .lianlian_api import request
from .lianlian_config import config
from .util import now_to_str


def pay_to_bankcard(no_order, money_order, info_order, notify_url, bankcard):
    """ 代付
    :param no_order: 订单号
    :param money_order: 金额
    :param info_order: 原因
    :param notify_url: 回调通知url
    :param bankcard: 代付到此银行卡
    :return:
    """
    params = {
        'platform': config.platform,
        'oid_partner': config.oid_partner,
        'sign_type': config.sign_type.RSA,
        'no_order': no_order,
        'dt_order': now_to_str(),
        'money_order': money_order,
        'info_order': info_order,
        'flag_card': unicode(bankcard.flag),
        'card_no': bankcard.card_no,
        'acct_name': bankcard.account_name,
        'bank_code': bankcard.bank_code,
        'province_code': bankcard.province_code,
        'city_code': bankcard.city_code,
        'brabank_name': bankcard.branch_bank_name,
        'notify_url': notify_url,
        'api_version': '1.2',
        'prcptcd': ''
    }
    # TODO:
    # note: bankcode, 对公必须传
    # note: province_code, city_code, brabank_name, 工、农、中, 招,光大 浦发(对私打款),建行 (对公打款)可以不传, 其他银行必须传
    return request(config.pay_to_bankcard.url, params)
