# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import requests
from .error import *
from . import signer


def sign_params(params):
    params = {unicode(k): unicode(v) for k, v in params.items()}
    params['sign'] = signer.sign(params, params['sign_type'])

    return params


def request(api_url, params):
    data = json.dumps(sign_params(params))

    resp = requests.post(api_url, data)
    if resp.status_code == 200:
        return _parse_response_data(resp.content)
    return UnExpectedResponseError(resp.status_code, resp.content)


def parse_and_verify_request_data(values, raw_data):
    parsed_data = values if values else _parse_data(raw_data)

    if _verify_sign(parsed_data):
        return parsed_data
    else:
        raise InvalidSignError(parsed_data.get('sign_type'), parsed_data)


def _verify_sign(data):
    return 'sign_type' in data and signer.verify(data, data['sign_type'])


def _parse_data(raw_data):
    data = json.loads(raw_data)
    if not isinstance(data, dict):
        raise DictParsingError(raw_data)
    return data


def _parse_response_data(raw_data):
    try:
        parsed_data = _parse_data(raw_data)
    except Exception, e:
        raise ApiError(str(e))

    if 'sign_type' not in parsed_data or not signer.verify(parsed_data, parsed_data['sign_type']):
        InvalidSignError(parsed_data.get('sign_type'), parsed_data)

    return parsed_data
