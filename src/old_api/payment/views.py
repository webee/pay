# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from decimal import Decimal
import logging
import requests

from old_api.util import response
from flask import jsonify, request, Response, redirect
from . import pay_mod as mod
from .prepay import Order, find_or_create_prepay_transaction
from .pay import pay_by_uuid, PaymentNotFoundError
from .postpay import *
from .confirm_pay import confirm_payment
from old_api.account.account.dba import get_account_by_id
from old_api.util.enum import enum
from old_api.util.ipay.transaction import generate_pay_url, is_sending_to_me, notification, parse_and_verify

logger = logging.getLogger(__name__)

PayResult = enum(Success=0, Failure=1, IsInvalidRequest=2)


@mod.route('/pre-pay', methods=['POST'])
def prepay():
    data = request.values
    client_id = data['client_id']
    payer_id = data['payer']
    payee_id = data['payee']
    order = Order(data['activity_id'], data['order_no'], data['order_name'], data['order_desc'], data['ordered_on'])
    amount = data['amount']
    client_callback_url = data['client_callback_url']
    client_async_callback_url = data['client_async_callback_url']

    payment_id = find_or_create_prepay_transaction(client_id, payer_id, payee_id, order,
                                                   amount, client_callback_url, client_async_callback_url)
    pay_url = generate_pay_url(payment_id)

    return jsonify({'pay_url': pay_url})


@mod.route('/pay/<uuid>', methods=['GET'])
def pay(uuid):
    try:
        form_submit = pay_by_uuid(uuid)
        return Response(form_submit, status=200, mimetype='text/html')
    except PaymentNotFoundError:
        return response.not_found({'uuid': uuid})


@mod.route('/pay/<uuid>/result', methods=['POST'])
@parse_and_verify
def post_pay_result(uuid):
    result = _notify_payment_result(uuid, request.verified_data)

    if result == PayResult.IsInvalidRequest:
        return notification.is_invalid
    elif result == PayResult.Failure:
        return notification.fail
    callback_url = _construct_pay_result_callback_url(uuid, callback_url_key='client_callback_url')
    return redirect(callback_url)



@mod.route('/pay/<uuid>/notify', methods=['POST'])
@parse_and_verify
def notify_payment(uuid):
    result = _notify_payment_result(uuid, request.verified_data)
    if result == PayResult.IsInvalidRequest:
        return notification.is_invalid()
    elif result == PayResult.Failure:
        return notification.fail()
    callback_url = _construct_pay_result_callback_url(uuid, callback_url_key='client_async_callback_url')
    resp = requests.put(callback_url)
    if resp.status_code == 200:
        data = resp.json()
        if data['code'] == 0 or data['code'] == '0':
            return notification.succeed()
    return notification.fail()


def _notify_payment_result(uuid, data):
    partner_oid = data['oid_partner']
    order_no = data['no_order']
    amount = Decimal(data['money_order'])
    pay_result = data['result_pay']
    paybill_oid = data['oid_paybill']

    if (not is_sending_to_me(partner_oid)) or (not is_valid_payment(order_no, uuid, amount)):
        return PayResult.IsInvalidRequest

    if not is_successful_payment(pay_result):
        fail_payment(order_no)
        return PayResult.Failure

    succeed_payment(order_no, paybill_oid)
    return PayResult.Success


def _construct_pay_result_callback_url(uuid, callback_url_key='client_callback_url'):
    pay_record = find_payment_by_uuid(uuid)
    account = get_account_by_id(pay_record['payer_account_id'])
    return '{0}?user_id={1}&order_id={2}&amount={3}&status=money_locked'.format(pay_record[callback_url_key],
                                                                                account['user_id'],
                                                                                pay_record['order_id'],
                                                                                pay_record['amount'])