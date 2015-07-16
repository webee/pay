# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import requests
from .lianlian_config import config

from .sign import sign, verify


def sign_params(params):
    params = {unicode(k): unicode(v) for k, v in params.items()}
    params['sign'] = sign(params, params['sign_type'])

    return params


def md5_sign_params(params):
    params['sign_type'] = config.sign_type.MD5

    return sign_params(params)


def rsa_sign_params(params):
    params['sign_type'] = config.sign_type.RSA

    return sign_params(params)


def request(api_url, params):
    data = json.dumps(sign_params(params))

    req = requests.post(api_url, data)
    if req.status_code == 200:
        return _parse_response_data(req.content)
    return {'ret': False, 'msg': 'api http request failed.'}


def parse_request_data(raw_data):
    parsed_data = _parse_data(raw_data)
    data = None
    msg = None
    if parsed_data['ret']:
        ret_data = parsed_data['data']
        if 'sign_type' in ret_data and verify(ret_data, ret_data['sign_type']):
            data = ret_data
        else:
            msg = "数据签名错误"
    else:
        msg = parsed_data['msg']

    if data:
        return {'ret': True, 'data': data}
    return {'ret': False, 'msg': msg}


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
        return {'ret': True, 'data': data}
    return {'ret': False, 'msg': msg}


def _parse_response_data(raw_data):
    parsed_data = _parse_data(raw_data)
    data = None
    code = None
    msg = None
    if parsed_data['ret']:
        ret_data = parsed_data['data']
        if 'ret_code' in ret_data and ret_data['ret_code'] == '0000':
            if 'sign_type' in ret_data:
                if verify(ret_data, ret_data['sign_type']):
                    data = ret_data
                else:
                    msg = "数据签名错误"
            else:
                data = {'ret_code': ret_data['ret_code'], 'ret_msg': ret_data.get('ret_msg')}
        else:
            code = ret_data.get('ret_code')
            msg = ret_data.get('ret_msg')
    else:
        msg = parsed_data['msg']

    if data:
        return {'ret': True, 'data': data}
    return {'ret': False, 'code': code, 'msg': msg}
