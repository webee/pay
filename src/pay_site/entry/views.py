# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from flask import request, render_template, redirect, url_for
import logging
from . import entry_mod as mod
from datetime import datetime
import client_info
from pay_site.trade.utils import format_string

log = logging.getLogger(__name__)


@mod.route('/')
def index():
    return render_template('index.html')


@mod.route('/pay/', methods=['GET', 'POST'])
def pay():
    if request.method == 'GET':
        order_id = 'T%s' % datetime.now().strftime('%Y%m%d%H%M%S')
        return render_template('pay.html',
                               client_id=client_info.client_id,
                               order_id=order_id,
                               to_account_id=client_info.to_account_id)
    elif request.method == 'POST':
        data = request.form

        client_id = client_info.client_id
        order_id = format_string(data.get('order_id'))

        product_name = format_string(data.get('product_name'))
        product_category = format_string(data.get('product_category'))
        product_desc = format_string(data.get('product_desc'))

        user_source = format_string(data.get('user_source'))
        user_id = format_string(data.get('user_id'))

        to_account_id = client_info.to_account_id
        amount = float(format_string(data.get('amount', '0')))

        return redirect(url_for('trade.pay', client_id=client_id,
                                order_id=order_id,
                                product_name=product_name,
                                product_category=product_category,
                                product_desc=product_desc,
                                user_source=user_source,
                                user_id=user_id,
                                to_account_id=to_account_id,
                                amount=amount))
