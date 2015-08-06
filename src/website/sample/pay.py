# -*- coding: utf-8 -*-
from datetime import datetime

import requests
from pytoolbox import config
from website.util.uuid import encode_uuid


_API_HOST = config.get('hosts', 'api_gateway')
_SITE_HOST = config.get('hosts', 'site_gateway')


def pay(amount):
    order_no = _generate_order_id()
    params = {
        'client_id': 1,
        'payer': 2001,
        'payee': 1001,
        'activity_id': '200001',
        'order_no': order_no,
        'order_name': 'Christmas gift',
        'order_desc': 'Gift to my friend',
        'ordered_on': datetime(2015, 6, 19, 18, 28, 35),
        'amount': amount,
        'client_callback_url': '{0}/pay/{1}/notify-result'.format(_SITE_HOST, order_no),
        'client_async_callback_url': '{0}/pay/{1}/notify-result'.format(_SITE_HOST, order_no)
    }
    return requests.post('{0}/secured/pre-pay'.format(_API_HOST), data=params)


def response_pay_result_notification(order_no):
    params = {
        'oid_partner': '201507021000395502',
        'no_order': order_no,
        'money_order': 1.0,
        'result_pay': 'SUCCESS',
        'oid_paybill': '123456789'
    }
    uuid = encode_uuid(order_no)
    return requests.post('{0}/secured/pay/{1}/result'.format(_API_HOST, uuid), data=params)


def _generate_order_id():
    return datetime.now().strftime("%Y%m%d%H%M%S%f")
