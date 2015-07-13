# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import render_template, redirect
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
    params = {
        'client_id': 1,
        'payer': 2001,
        'payee': 1001,
        'order_no': 111111,
        'order_name': 'Christmas gift',
        'order_desc': 'Gift to my friend',
        'ordered_on': datetime.now(),
        'amount': 0.01
    }
    resp = requests.post('http://localhost:5000/pre-pay', data=params)
    if resp.status_code == 200:
        content = resp.json()
        return redirect(content['pay_url'])
    return render_template('omnipotent.html', pay_result='SUCCESS')
