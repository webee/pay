# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

from . import pay_mod as mod
from .prepay import Order, find_or_create_account, generate_prepay_order, build_pay_url
from flask import jsonify, request, redirect


log = logging.getLogger(__name__)


@mod.route('/pre-pay', methods=['POST'])
def prepay():
    args = request.args
    client_id = args['client_id'] or 1
    payer_id = args['payer']
    payee_id = args['payee'] or '1001'
    order = Order(args['order_no'], args['order_name'], args['order_desc'], args['ordered_on'])
    amount = args['amount']

    pay_uuid = generate_prepay_order(client_id, payer_id, payee_id, order, amount)
    pay_url = build_pay_url(pay_uuid)

    return jsonify({})


@mod.route('/pay/<uuid>', methods=['GET'])
def pay(uuid):
    return jsonify({})


@mod.route('/pay-result', methods=['POST'])
def notify_payment():
    return jsonify({})
