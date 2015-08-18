# coding=utf-8
from __future__ import unicode_literals

from flask import url_for, Response
from api_x.config import test_pay
import requests
from .commons import generate_absolute_url

NAME = 'TEST_PAY'


def pay(source, user_id, order_no, product_name, amount):
    return_url = test_pay.ROOT_URL + url_for('test_pay_entry.pay_result', pay_source=source)
    notify_url = test_pay.ROOT_URL + url_for('test_pay_entry.pay_notify', pay_source=source)
    params = {
        'merchant_id': test_pay.MERCHANT_ID,
        'user_id': user_id,
        'order_no': order_no,
        'product_name': product_name,
        'amount': amount,
        'return_url': return_url,
        'notify_url': notify_url
    }

    return Response(generate_submit_form(test_pay.Pay.URL, params))


def generate_submit_form(url, req_params):
    submit_page = '<form id="returnForm" action="{0}" method="POST">'.format(url)
    for key in req_params:
        submit_page += '''<input type="hidden" name="{0}" value='{1}' />'''.format(key, req_params[key])
    submit_page += '<input type="submit" value="Submit" style="display:none" /></form>'
    submit_page += '<script>document.forms["returnForm"].submit();</script>'
    return submit_page


def refund(source, refund_no, amount, pay_sn, result='SUCCESS'):
    notify_url = generate_absolute_url(url_for('test_pay_entry.refund_notify', refund_source=source))
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
    notify_url = generate_absolute_url(url_for('test_pay_entry.pay_to_bankcard_notify', refund_source=source))
    params = {
        'merchant_id': test_pay.MERCHANT_ID,
        'order_no': order_no,
        'amount': amount,
        'notify_url': notify_url,
        'result': result
    }
    req = requests.post(test_pay.PayToBankcard.URL, params)

    return req.json()
