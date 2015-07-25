# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

import requests
from flask import render_template, redirect, request

from . import sample_mod as mod
from .pay import pay, response_pay_result_notification
from .refund import refund
from tools.mylog import get_logger

logger = get_logger(__name__)


@mod.route('/')
def index():
    return render_template('omnipotent.html')


@mod.route('/pay-one-cent', methods=['POST'])
def pay_one_cent():
    resp = pay(0.01)
    if resp.status_code == 200:
        content = resp.json()
        return redirect(content['pay_url'])
    return redirect('/')


@mod.route('/pay-result', methods=['POST'])
def pay_result():
    order_no = request.values['order_no']
    resp = response_pay_result_notification(order_no)
    if resp.status_code == 200:
        result = 'SUCCESS'
    else:
        result = 'FAILED'
    return render_template('omnipotent.html', execution_result=result)


@mod.route('/refund-one-cent', methods=['POST'])
def refund_one_cent():
    order_no = request.values['order_no']
    resp = refund(order_no)
    refund_result = 'FAILURE'
    if resp.status_code == 200:
        refund_result = 'SUCCESS'
    return render_template('omnipotent.html', execution_result=refund_result)