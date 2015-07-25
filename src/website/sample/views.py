# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from datetime import datetime

import requests
from flask import render_template, redirect, request
from website.util.uuid import encode_uuid
from . import sample_mod as mod
from tools.mylog import get_logger

logger = get_logger(__name__)


@mod.route('/')
def index():
    return render_template('omnipotent.html')


@mod.route('/pay-one-cent', methods=['POST'])
def pay_one_cent():
    order_no = 111112
    params = {
        'client_id': 1,
        'payer': 2001,
        'payee': 1001,
        'order_no': order_no,
        'order_name': 'Christmas gift',
        'order_desc': 'Gift to my friend',
        'ordered_on': datetime(2015, 6, 18, 18, 28, 35),
        'amount': 0.01,
        'success_return_url': 'http://localhost:5001/site/sample/pay/{0}/success'.format(order_no)
    }
    resp = requests.post('http://localhost:5000/pre-pay', data=params)
    if resp.status_code == 200:
        content = resp.json()
        return redirect(content['pay_url'])
    return render_template('omnipotent.html', execution_result='SUCCESS')


@mod.route('/pay-result', methods=['POST'])
def pay_result():
    data = request.values
    order_no = data['order_no']
    params = {
        'oid_partner': '201507021000395502',
        'no_order': order_no,
        'money_order': 1.0,
        'result_pay': 'SUCCESS',
        'oid_paybill': '123456789'
    }
    uuid = encode_uuid(order_no)
    resp = requests.post('http://localhost:5000/pay/{0}/result'.format(uuid), data=params)
    if resp.status_code == 200:
        result = 'SUCCESS'
    else:
        result = 'FAILED'
    return render_template('omnipotent.html', execution_result=result)


@mod.route('/refund-one-cent', methods=['POST'])
def refund_one_cent():
    params = {
        'client_id': 1,
        'payer': 2001,
        'order_no': 111112,
        'amount': 0.01
    }
    resp = requests.post('http://localhost:5000/refund', data=params)
    refund_result = 'FAILURE'
    if resp.status_code == 200:
        refund_result = 'SUCCESS'
    return render_template('omnipotent.html', execution_result=refund_result)