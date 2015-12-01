# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import requests
from ..error import *
from . import signer
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


def sign_params(params):
    params = {unicode(k): unicode(v) for k, v in params.items()}
    params['sign'] = signer.sign(params, params['sign_type'])

    return params


def request(api_url, params, pass_verify=False):
    data = json.dumps(sign_params(params))

    logger.info("request {0}: {1}".format(api_url, data))
    resp = requests.post(api_url, data)
    if resp.status_code == 200:
        try:
            raw_data = resp.content.decode('utf-8')
        except Exception as e:
            raise DataEncodingError(e.message)
        logger.info("response {0}: {1}".format(api_url, raw_data))
        return _parse_and_verify_response_data(raw_data, pass_verify)
    return UnExpectedResponseError(resp.status_code, resp.content)


def parse_and_verify_request_data(values, raw_data):
    parsed_data = values if values else _parse_data(raw_data)

    logger.info("requested : %r" % parsed_data)
    if _verify_sign(parsed_data, do_raise=True):
        return parsed_data


def _verify_sign(data, do_raise=False):
    if 'sign_type' in data and signer.verify(data, data['sign_type']):
        return True
    if do_raise:
        raise InvalidSignError(data.get('sign_type'), data)
    return False


def _parse_data(raw_data):
    data = json.loads(raw_data)
    if not isinstance(data, dict):
        raise DictParsingError(raw_data)
    return data


def _parse_and_verify_response_data(raw_data, pass_verify=False):
    try:
        parsed_data = _parse_data(raw_data)
    except Exception, e:
        raise ApiError(str(e))

    if not ('ret_code' in parsed_data and parsed_data['ret_code'] == '0000'):
        raise ApiError('ret_code: [{0}], ret_msg: [{1}]'.format(parsed_data.get('ret_code'), parsed_data.get('ret_msg')),
                       data=parsed_data)

    if not pass_verify:
        _verify_sign(parsed_data, do_raise=True)

    return parsed_data
