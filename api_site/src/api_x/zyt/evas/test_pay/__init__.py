# coding=utf-8
from __future__ import unicode_literals

from flask import url_for, Response
from api_x.config import test_pay
import requests
from .commons import generate_absolute_url
from api_x.config import test_pay as config
from ..error import PaymentTypeNotSupportedError

NAME = 'TEST_PAY'


def payment_param(payment_type, source, user_id, order_no, product_name, amount):
    common_params = _get_common_params(source, user_id, order_no, product_name, amount)
    if payment_type == config.PaymentType.WEB:
        return_url = test_pay.ROOT_URL + url_for('test_pay_entry.pay_result', source=source)
        params = {
            'return_url': return_url
        }
        params.update(common_params)
        return params
    elif payment_type == config.PaymentType.APP:
        return common_params
    else:
        raise PaymentTypeNotSupportedError(NAME, payment_type)


def pay(source, user_id, order_no, product_name, amount, channel=None):
    if channel in [config.Pay.Channel.APP, config.Pay.Channel.API]:
        # app请求参数
        return _get_common_params(source, user_id, order_no, product_name, amount)

    return_url = test_pay.ROOT_URL + url_for('test_pay_entry.pay_result', source=source)
    params = {
        'return_url': return_url
    }
    params.update(_get_common_params(source, user_id, order_no, product_name, amount))
    return Response(generate_submit_form(test_pay.Pay.URL, params))


def _get_common_params(source, user_id, order_no, product_name, amount):
    notify_url = test_pay.ROOT_URL + url_for('test_pay_entry.pay_notify', source=source)
    params = {
        'merchant_id': test_pay.MERCHANT_ID,
        'user_id': user_id,
        'order_no': order_no,
        'product_name': product_name,
        'amount': str(amount),
        'notify_url': notify_url,
        '_url': test_pay.Pay.URL
    }

    return params


def generate_submit_form(url, req_params):
    submit_page = '<form id="returnForm" action="{0}" method="POST">'.format(url)
    for key in req_params:
        if key.startswith('_'):
            continue
        submit_page += '''<input type="hidden" name="{0}" value='{1}' />'''.format(key, req_params[key])
    submit_page += '<input type="submit" value="Submit" style="display:none" /></form>'
    submit_page += '<script>document.forms["returnForm"].submit();</script>'
    return submit_page


def refund(source, refund_no, amount, pay_sn, result='SUCCESS'):
    notify_url = generate_absolute_url(url_for('test_pay_entry.refund_notify', source=source))
    params = {
        'merchant_id': test_pay.MERCHANT_ID,
        'refund_no': refund_no,
        'amount': amount,
        'pay_sn': pay_sn,
        'notify_url': notify_url,
        'result': result
    }
    req = requests.post(test_pay.Refund.URL, params)

    return req.json()


def pay_to_bankcard(source, order_no, amount, result='SUCCESS'):
    notify_url = generate_absolute_url(url_for('test_pay_entry.pay_to_bankcard_notify', source=source))
    params = {
        'merchant_id': test_pay.MERCHANT_ID,
        'order_no': order_no,
        'amount': amount,
        'notify_url': notify_url,
        'result': result
    }
    req = requests.post(test_pay.PayToBankcard.URL, params)

    return req.json()
