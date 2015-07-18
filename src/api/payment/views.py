# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging
from decimal import Decimal

from . import pay_mod as mod
from .prepay import Order, generate_prepay_transaction
from .pay import pay_by_uuid
from .postpay import *
from api.util.ipay.transaction import generate_pay_url, is_sending_to_me, notification, parse_and_verify
from flask import jsonify, request, Response

log = logging.getLogger(__name__)


@mod.route('/pre-pay', methods=['POST'])
def prepay():
    data = request.values
    client_id = data['client_id']
    payer_id = data['payer']
    payee_id = data['payee']
    order = Order(data['order_no'], data['order_name'], data['order_desc'],
                  data['ordered_on'])
    amount = data['amount']

    payment_id = generate_prepay_transaction(client_id, payer_id, payee_id, order, amount)
    pay_url = generate_pay_url(payment_id)

    return jsonify({'pay_url': pay_url})


@mod.route('/pay/<uuid>', methods=['GET'])
def pay(uuid):
    form_submit = pay_by_uuid(uuid)
    return Response(form_submit, status=200, mimetype='text/html')


@mod.route('/pay/<uuid>/result', methods=['POST'])
@parse_and_verify
def notify_payment(uuid):
    data = request.verified_data
    partner_oid = data['oid_partner']
    order_no = data['no_order']
    amount = Decimal(data['money_order'])
    pay_result = data['result_pay']
    paybill_oid = data['oid_paybill']

    if (not is_sending_to_me(partner_oid)) or (not is_valid_payment(order_no, uuid, amount)):
        return notification.is_invalid()

    if not is_successful_payment(pay_result):
        fail_payment(order_no)
        return notification.fail()

    succeed_payment(order_no, paybill_oid)
    return notification.succeed()

