# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import render_template, redirect, url_for
from . import sample_mod as mod
from tools.mylog import get_logger

from datetime import datetime
import requests

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
    return render_template('omnipotent.html', pay_result='SUCCESS')


@mod.route('/pay/<order_no>/success')
def did_pay(order_no):
    return render_template('pay_result.html', order_no=order_no)


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
    return render_template('omnipotent.html', refund_result=refund_result)