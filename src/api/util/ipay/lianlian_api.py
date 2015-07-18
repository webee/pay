# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import requests

from .error import ApiError, InvalidSignError
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
    try:
        parsed_data = _parse_data(raw_data)
    except Exception, e:
        raise ApiError(str(e))

    if 'sign_type' in parsed_data and verify(parsed_data, parsed_data['sign_type']):
        return parsed_data
    else:
        raise InvalidSignError(parsed_data['sign_type'], parsed_data)


def _parse_data(raw_data):
    data = json.loads(raw_data)
    if not isinstance(data, dict):
        raise TypeError("Data [{0}] mst be a dict.".format(raw_data))

    return data


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
