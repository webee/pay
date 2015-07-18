# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import requests

from .error import ApiError, InvalidSignError, UnExpectedResponseError, RequestFailedError
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

    resp = requests.post(api_url, data)
    if resp.status_code == 200:
        return _parse_response_data(resp.content)
    return UnExpectedResponseError(resp.status_code, resp.content)


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
    try:
        parsed_data = _parse_data(raw_data)
    except Exception, e:
        raise ApiError(str(e))

    if 'ret_code' not in parsed_data or parsed_data['ret_code'] != '0000':
        raise RequestFailedError(parsed_data.get('ret_code'), parsed_data.get('ret_msg'))

    if 'sign_type' not in parsed_data or not verify(parsed_data, parsed_data['sign_type']):
        InvalidSignError(parsed_data.get('sign_type'), parsed_data)

    return parsed_data
