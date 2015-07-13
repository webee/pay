# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

from . import pay_mod as mod
from .prepay import Order, save_pay_info, build_pay_url
from flask import jsonify, request, redirect


log = logging.getLogger(__name__)


@mod.route('/pre-pay', methods=['POST'])
def prepay():
    args = request.args
    user_id = args['user_id']
    order = Order(args['order_no'], args['order_name'], args['order_desc'], args['ordered_on'])
    amount = args['amount']
    pay_id = save_pay_info(user_id, order, amount)
    pay_url = build_pay_url(pay_id)

    return redirect(pay_url) #?????


@mod.route('/pay/<uuid>', methods=['GET'])
def pay(uuid):
    return jsonify({})


@mod.route('/pay-result', methods=['POST'])
def notify_payment():
    return jsonify({})
