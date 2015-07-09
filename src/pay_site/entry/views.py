# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging
from datetime import datetime

from flask import request, render_template, redirect, url_for, jsonify, current_app
from . import entry_mod as mod
from pay_site import test_client_info
from tools.utils import format_string
import requests

logger = logging.getLogger(__name__)


@mod.route('/')
def index():
    return render_template('index.html')


@mod.route('/pay/', methods=['GET', 'POST'])
def pay():
    if request.method == 'GET':
        order_id = 'T%s' % datetime.now().strftime('%Y%m%d%H%M%S')
        return render_template('pay.html',
                               client_id=test_client_info.client_id,
                               order_id=order_id,
                               to_account_id=test_client_info.to_account_id)
    elif request.method == 'POST':
        data = request.form

        order_id = format_string(data.get('order_id'))

        product_name = format_string(data.get('product_name'))
        product_category = format_string(data.get('product_category'))
        product_desc = format_string(data.get('product_desc'))

        user_source = format_string(data.get('user_source'))
        user_id = format_string(data.get('user_id'))

        to_account_id = test_client_info.to_account_id
        amount = float(format_string(data.get('amount', '0')))

        host_url = current_app.config.get('HOST_URL')
        callback_url = host_url + url_for('entry.pay_callback')
        params = {
            'client_id': test_client_info.client_id,
            'order_id': order_id,
            'product_name': product_name,
            'product_category': product_category,
            'product_desc': product_desc,
            'user_source': user_source,
            'user_id': user_id,
            'to_account_id': to_account_id,
            'amount': amount,
            'callback': callback_url,
            'web_callback': ""
        }

        pay_api_url = current_app.config['PAY_API_URL']
        req = requests.post(pay_api_url, params)
        result = req.json()

        payurl = result['payurl']
        return redirect(payurl)


@mod.route('/pay_callback/', methods=['POST'])
def pay_callback():
    data = request.form

    logger.info('pay_callback data: %s', str(data))
