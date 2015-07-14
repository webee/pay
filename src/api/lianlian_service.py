# coding=utf-8
from __future__ import unicode_literals
import json
import requests
from api import sign
from api.base_config import get_config


def request_api(api_url, params):
    """ 请求连连api入口方法
    :param api_url: api url.
    :param params: api参数，必须包含sign_type属性
    :return:
    """
    params['sign'] = sign.sign(params, params['sign_type'])
    data = json.dumps(params)

    req = requests.post(api_url, data)

    data = None
    code = None
    msg = None
    try:
        ret_data = req.json()
        if isinstance(ret_data, dict):
            if ret_data['ret_code'] == '0000':
                if sign.verify(ret_data, ret_data['sign_type']):
                    data = ret_data
                else:
                    msg = "数据签名错误"
            else:
                code = ret_data['ret_code']
                msg = ret_data['ret_msg']
        else:
            msg = "返回数据错误"
    except ValueError as e:
        msg = "返回数据错误"

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
