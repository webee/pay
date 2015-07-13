# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

from . import pay_mod as mod, config
from .prepay import Order, generate_prepay_order, build_pay_url
from flask import jsonify, request
from urlparse import urljoin

log = logging.getLogger(__name__)


@mod.route('/pre-pay', methods=['POST'])
def prepay():
    request_values = request.values
    client_id = request_values['client_id']
    payer_id = request_values['payer']
    payee_id = request_values['payee']
    order = Order(request_values['order_no'], request_values['order_name'], request_values['order_desc'],
                  request_values['ordered_on'])
    amount = request_values['amount']

    pay_uuid = generate_prepay_order(client_id, payer_id, payee_id, order, amount, _abs_url(config.payment.notify_url))
    pay_url = build_pay_url(pay_uuid)

    return jsonify({})


@mod.route('/pay/<uuid>', methods=['GET'])
def pay(uuid):
    return jsonify({})


@mod.route('/pay-result', methods=['POST'])
def notify_payment():
    return jsonify({})


def _abs_url(relative_url):
    return urljoin(request.url_root, relative_url)
