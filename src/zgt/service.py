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


def encrypt_parameters(params, hmac_orders):
    """加密发送参数
    :param params: 参数字典
    :param hmac_orders: hmac签名顺序
    :return: 加密之后的数据
    """
    customernumber = merchantInfo.customernumber
    data_map = {k: v for k, v in params.items()}
    data_map['customernumber'] = customernumber
    key_for_hmac = merchantInfo.keyValue
    key_for_aes = merchantInfo.keyValue[:16]

    string_array = [data_map.get(k, '') for k in hmac_orders]
    hmac = get_hmac(string_array, key_for_hmac)

    data_map['hmac'] = hmac
    data_json_string = json.dumps(data_map)
    data = aes_util.encrypt(data_json_string, key_for_aes)

    return {
        'customernumber': customernumber,
        'data': data
    }



def parse_data_from_yeepay(data, hmac_sign_order):
    """解密和解析易宝接口返回数据
    :param data: 加密数据
    :param hmac_sign_order: 参数hmac签名顺序
    :return:
    """
    key_for_hmac = merchantInfo.keyValue
    key_for_aes = merchantInfo.keyValue[:16]

    data_from_yeepay = format_string(data)
    decrypt_data = aes_util.decrypt(data_from_yeepay, key_for_aes)

    result = json.loads(decrypt_data)

    if 'msg' in result:
        return result

    hmac_yeepay = format_string(result.get('hmac'))
    string_array = [result.get(k, '') for k in hmac_sign_order]
    hmac_local = get_hmac(string_array, key_for_hmac)

    if hmac_local != hmac_yeepay:
        result['customError'] = "hmac_mismatch error."

    return result


def parse_http_response_body(status_code, body_content, hmac_encryption_order):
    result = {}
    if status_code != 200:
        result['customError'] = "Request failed, response code = " + status_code
        return result

    json_map = json.loads(body_content)

    if 'msg' in json_map:
        result = json_map
        return result

    logger.info('response body: %s', json_map)
    return parse_data_from_yeepay(json_map.get('data'), hmac_encryption_order)


def yeepay_api_request(request_url, request_params, hmac_orders, ret_hmac_orders):
    """易宝接口通用请求方法
    :param request_url: 接口url
    :param request_params: 参数字典
    :param hmac_orders: 签名顺序
    :param ret_hmac_orders: 接口返回参数签名顺序
    :return: 返回数据字典
    """
    params = encrypt_parameters(request_params, hmac_orders)

    req = requests.post(request_url, params)
    status_code = req.status_code
    content = req.content

    try:
        result = parse_http_response_body(status_code, content, ret_hmac_orders)
    except Exception as e:
        result = {"customError": "Caught an Exception - " + e.message}
    return result


def payment_request(request_params):
    """易宝支付接口
    :param request_params: 除customernumber外的其他参数
    :return: 接口返回结果或者错误结果
    """
    hmac_orders = ['customernumber', 'requestid', 'amount', 'assure', 'productname', 'productcat',
                   'productdesc', 'divideinfo', 'callbackurl', 'webcallbackurl', 'bankid', 'period', 'memo']

    request_url = merchantInfo.pay_url

    ret_hmac_order = ["customernumber", "requestid", "code", "externalid", "amount", "payurl"]

    return yeepay_api_request(request_url, request_params, hmac_orders, ret_hmac_order)


def payment_query(request_params):
    """易宝支付订单查询接口
    :param request_params: 除customernumber外的其他参数
    :return:
    """
    hmac_orders = ['customernumber', 'requestid']
    request_url = merchantInfo.query_order_url
    ret_hmac_order = ["customernumber", "requestid", "code", "externalid", "amount",
                      "productname", "productcat", "productdesc", "status", "ordertype",
                      "busitype", "orderdate", "createdate", "bankid"]

    return yeepay_api_request(request_url, request_params, hmac_orders, ret_hmac_order)


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
