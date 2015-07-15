# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

import requests
from api.util import sign


def request(api_url, params):
    params = {unicode(k): unicode(v) for k, v in params.items()}
    params['sign'] = sign.sign(params, params['sign_type'])
    data = json.dumps(params)

    req = requests.post(api_url, data)

    return _parse_response_data(req.content)


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


def _parse_response_data(raw_data):
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
