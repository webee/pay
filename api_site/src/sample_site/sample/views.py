# coding=utf-8
from __future__ import unicode_literals, print_function

from flask import request, render_template, redirect, url_for
from . import sample_mod as mod
import requests
from sample_site import config
from sample_site.utils import generate_order_id


@mod.route('/pay', methods=['GET', 'POST'])
def pay():
    """支付一分钱"""
    if request.method == 'GET':
        return render_template('sample/pay.html')

    params = {
        'channel_id': 1,
        'payer_user_id': 'webee',
        'payee_user_id': 'test001',
        'order_id': generate_order_id(),
        'product_name': '支付1分钱',
        'product_category': '测试',
        'product_desc': '用于测试的商品',
        'amount': 0.01,
        'client_callback_url': config.HOST_URL + url_for('.pay'),
        'client_notify_url': '',
        'payment_type': request.values['payment_type']
    }

    print("order_id: {0}".format(params['order_id']))

    req = requests.post(config.PayAPI.PRE_PAY_URL, params)
    data = req.json()
    return redirect(data['pay_url'])


@mod.route('/pay/guarantee_payment/confirm', methods=['POST'])
def confirm_guarantee_payment():
    params = {
        'channel_id': 1,
        'order_id': request.values['order_id']
    }

    req = requests.post(config.PayAPI.CONFIRM_GUARANTEE_PAYMENT_URL, params)
    data = req.json()
    print('ret: {0}'.format(data))
    return redirect(url_for('sample.pay'))


@mod.route('/prepaid', methods=['GET'])
def prepaid():
    """充值"""
    return render_template('sample/prepaid.html', user_id=2, prepaid_url=config.PayAPI.PREPAID_URL)