# coding=utf-8
from __future__ import unicode_literals
import json
from datetime import datetime

import requests
from api.util import sign
from api.base_config import get_config


def _parse_data(raw_data):
    data = None
    try:
        ret_data = json.loads(raw_data)
        if isinstance(ret_data, dict):
            data = ret_data
        else:
            msg = "数据错误"
    except ValueError as e:
        msg = "数据错误"
    if data:
        return {
            'ret': True,
            'data': data
        }
    else:
        return {
            'ret': False,
            'msg': msg
        }


def parse_request_data(raw_data):
    parsed_data = _parse_data(raw_data)
    data = None
    msg = None
    if parsed_data['ret']:
        ret_data = parsed_data['data']
        if 'sign_type' in ret_data and sign.verify(ret_data, ret_data['sign_type']):
            data = ret_data
        else:
            msg = "数据签名错误"
    else:
        msg = parsed_data['msg']

    if data:
        return {
            'ret': True,
            'data': data
        }
    else:
        return {
            'ret': False,
            'msg': msg
        }


def parse_response_data(raw_data):
    parsed_data = _parse_data(raw_data)
    data = None
    code = None
    msg = None
    if parsed_data['ret']:
        ret_data = parsed_data['data']
        if 'ret_code' in ret_data and ret_data['ret_code'] == '0000':
            if sign.verify(ret_data, ret_data['sign_type']):
                data = ret_data
            else:
                msg = "数据签名错误"
        else:
            code = ret_data.get('ret_code')
            msg = ret_data.get('ret_msg')
    else:
        msg = parsed_data['msg']

    if data:
        return {
            'ret': True,
            'data': data
        }
    else:
        return {
            'ret': False,
            'code': code,
            'msg': msg
        }


def request_api(api_url, params):
    """ 请求连连api入口方法
    :param api_url: api url.
    :param params: api参数，必须包含sign_type属性, 且所有参数为字符串
    :return:
    """
    params = {unicode(k): unicode(v) for k, v in params.items()}
    params['sign'] = sign.sign(params, params['sign_type'])
    data = json.dumps(params)

    req = requests.post(api_url, data)

    return parse_response_data(req.content)


def bankcard_query(card_no):
    """ 查询银行卡bin信息
    :param card_no: 银行卡号
    :return:
    """
    config = get_config()
    params = {
        'oid_partner': config.oid_partner,
        'sign_type': config.sign_type.MD5,
        'card_no': card_no
    }

    api_url = "https://yintong.com.cn/traderapi/bankcardquery.htm"
    return request_api(api_url, params)


def get_current_dt_str():
    now = datetime.now()
    return now.strftime('%Y%m%d%H%M%S')


def withdraw(no_order, money_order, info_order, notify_url, bankcard):
    """ 代付
    :param no_order: 订单号
    :param money_order: 金额
    :param info_order: 原因
    :param notify_url: 回调通知url
    :param bankcard: 代付到此银行卡
    :return:
    """
    config = get_config()

    params = {
        'platform': config.platform,
        'oid_partner': config.oid_partner,
        'sign_type': config.sign_type.RSA,
        'no_order': no_order,
        'dt_order': get_current_dt_str(),
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
        'api_version': "1.2",
        'prcptcd': ''
    }
    # note: bankcode, 对公必须传
    # note: province_code, city_code, brabank_name, 工、农、中, 招,光大 浦发(对私打款),建行 (对公打款)可以不传, 其他银行必须传

    api_url = "https://yintong.com.cn/traderapi/cardandpay.htm"
    return request_api(api_url, params)


def query_order():
    # TODO:
    config = get_config()

    params = {
        'platform': config.platform,
        'oid_partner': config.oid_partner,
    }


    api_url ="https://yintong.com.cn/traderapi/orderquery.htm",
    return request_api(api_url, params)
