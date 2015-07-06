# coding=utf-8
from __future__ import print_function, unicode_literals
import json

import requests

import digest
import merchantInfo
import aes_util
from tools.mylog import get_logger

logger = get_logger(__name__)


def get_hmac(arr, key):
    return digest.hmac_sign(''.join(arr), key)


def format_string(text):
    return "" if not text else text.strip()


def parse_data_from_yeepay(data, hmac_encryption_order):
    key_for_hmac = merchantInfo.keyValue
    key_for_aes = merchantInfo.keyValue[:16]

    data_from_yeepay = format_string(data)
    decrypt_data = aes_util.decrypt(data_from_yeepay, key_for_aes)

    result = json.loads(decrypt_data)

    if 'msg' in result:
        return result

    hmac_yeepay = format_string(result.get('hmac'))
    string_array = [result.get(k, '') for k in hmac_encryption_order]
    hmac_local = get_hmac(string_array, key_for_hmac)

    if hmac_local != hmac_yeepay:
        result['customError'] = "hmac_mismatch error."

    return result


def parse_http_response_body(status_code, response_body, hmac_encryption_order):
    result = {}
    if status_code != 200:
        result['customError'] = "Request failed, response code = " + status_code
        return result

    json_map = json.loads(response_body)

    if 'msg' in json_map:
        result = json_map
        return result

    return parse_data_from_yeepay(json_map.get('data'), hmac_encryption_order)


def payment_request(request_params):
    hmac_orders = ['customernumber', 'requestid', 'amount', 'assure', 'productname', 'productcat',
                   'productdesc', 'divideinfo', 'callbackurl', 'webcallbackurl', 'bankid', 'period', 'memo']

    customernumber = merchantInfo.customernumber
    request_params['customernumber'] = customernumber
    key_for_hmac = merchantInfo.keyValue
    key_for_aes = merchantInfo.keyValue[:16]

    string_array = [request_params.get(k, u'') for k in hmac_orders]
    hmac = get_hmac(string_array, key_for_hmac)

    data_map = request_params.copy()
    data_map['hmac'] = hmac
    data_json_string = json.dumps(data_map)
    data = aes_util.encrypt(data_json_string, key_for_aes)

    request_url = merchantInfo.requestURL

    params = {
        'customernumber': customernumber,
        'data': data
    }

    req = requests.post(request_url, params)
    status_code = req.status_code
    content = req.content
    hmac_encryption_order = ["customernumber", "requestid", "code", "externalid", "amount", "payurl"]

    try:
        result = parse_http_response_body(status_code, content, hmac_encryption_order)
    except Exception as e:
        result = {"customError": "Caught an Exception - " + e.message}

    return result


if __name__ == '__main__':
    data_map = {'webcallbackurl': 'http://localhost:8080/zgt-api-demo/jsp/callback.jsp', 'mcc': '7993', 'assure': '0', 'payproducttype': 'ONEKEY',
                'amount': '0.01', 'customernumber': '10012438801', 'productname': 'productname哈哈测试喵喵喵', 'productcat': 'productcat',
                'callbackurl': 'http://localhost:8080/zgt-java/jsp/callback.jsp', 'productdesc': 'productdesc',
                'hmac': '3638276f1e4422369b7dd01628e596e4', 'requestid': 'ZGTPAY150701_024038019'}

    hmac_orders = ['customernumber', 'requestid', 'amount', 'assure', 'productname', 'productcat',
                   'productdesc', 'divideinfo', 'callbackurl', 'webcallbackurl', 'bankid', 'period', 'memo']

    key_for_hmac = merchantInfo.keyValue

    string_array = [data_map.get(k, u'') for k in hmac_orders]
    hmac = get_hmac(string_array, key_for_hmac)

    logger.info('value: %s', ''.join(string_array))
    logger.info('key: %s', key_for_hmac)
    logger.info('hmac: %s', hmac)
