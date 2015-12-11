# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import xmltodict
import requests
from ..error import *
from . import signer
from .commons import verify_sign
from pytoolbox.util.sign import RSASignType
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


def sign_params(params):
    params = {unicode(k): unicode(v) for k, v in params.items()}
    params['sign'] = signer.sign(params, params['sign_type'], sign_type=RSASignType.SHA, urlsafe=True)

    return params


def request(api_url, params):
    data = sign_params(params)

    logger.info("request {0}: {1}".format(api_url, data))
    resp = requests.post(api_url, data)

    if resp.status_code == 200:
        try:
            raw_data = resp.content.decode('utf-8')
        except Exception as e:
            raise DataEncodingError(e.message)
        logger.info("response : %s: %s" % (api_url, raw_data))
        return _parse_and_verify_response_data(raw_data)
    return UnExpectedResponseError(resp.status_code, resp.content)


def parse_and_verify_request_data(data):
    logger.info("requested : %r" % data)
    if _verify_sign(data, do_raise=True):
        return data


def _verify_sign(data, do_raise=False):
    if 'sign_type' in data and signer.verify(data, data['sign_type'], sign_type=RSASignType.SHA, urlsafe=True):
        return True
    if do_raise:
        raise InvalidSignError(data.get('sign_type'), data)
    return False


def _parse_data(raw_data):
    """ raw_data必须是unicode
    :type raw_data: unicode
    :return:
    """
    res = xmltodict.parse(raw_data, encoding='utf-8')
    if not isinstance(res, dict) or 'alipay' not in res:
        raise DictParsingError(raw_data)
    data = res['alipay']

    is_success = data.get('is_success')
    if is_success == 'F' or is_success not in ['T', 'P']:
        raise ApiError(data.get('error', '接口请求异常'))

    return data


def _parse_and_verify_response_data(raw_data):
    parsed_data = _parse_data(raw_data)

    if 'response' in parsed_data and 'trade' in parsed_data['response']:
        resp_data = parsed_data['response']['trade']
        resp_data['sign_type'] = parsed_data['sign_type']
        resp_data['sign'] = parsed_data['sign']
        if verify_sign(resp_data, do_raise=True):
            return resp_data
    return parsed_data
