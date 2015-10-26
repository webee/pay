# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from api_x.zyt.evas.weixin_pay.commons import append_md5_sign, verify_sign

import xmltodict
import requests
from ..error import *
from api_x.config import weixin_pay as config
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


def request(api_url, params, app='main'):
    params = append_md5_sign(app, params)

    data = _params_to_xml(params)
    headers = {'Content-Type': 'application/xml'}

    logger.info("request {0}: {1}".format(api_url, data))
    resp = requests.post(api_url, data.encode('utf-8'), headers=headers)
    if resp.status_code == 200:
        try:
            raw_data = resp.content.decode('utf-8')
        except Exception as e:
            raise ResponseEncodingError(e.message)
        logger.info("response : {0}: {1}".format(api_url, raw_data))
        return _parse_and_verify_response_data(raw_data, app)
    return UnExpectedResponseError(resp.status_code, resp.content)


def parse_and_verify_request_data(raw_data, app):
    parsed_data = _parse_data(raw_data)

    if verify_sign(app, parsed_data, do_raise=True):
        return parsed_data


def _parse_data(raw_data):
    res = xmltodict.parse(raw_data, encoding='utf-8')
    if not isinstance(res, dict) or 'xml' not in res:
        raise DictParsingError(raw_data)
    data = res['xml']

    if data.get('return_code') != 'SUCCESS':
        raise ApiError(data.get('return_msg', '接口请求异常'))

    return data


def _parse_and_verify_response_data(raw_data, app):
    parsed_data = _parse_data(raw_data)

    if verify_sign(app, parsed_data, do_raise=True):
        return parsed_data


def _params_to_xml(params):
    d = {'xml': params}

    # FIXME: 非线上时pretty
    pretty = config.__env_name__ != 'prod'
    return xmltodict.unparse(d, full_document=False, pretty=pretty)


def response_xml(params):
    return _params_to_xml(params)
