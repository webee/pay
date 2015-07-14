# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging
from urlparse import urljoin
from decimal import Decimal

from . import pay_mod as mod, config
from .prepay import Order, generate_prepay_transaction
from .pay import pay_by_uuid
from .postpay import *
from flask import jsonify, request, Response


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

    transaction_uuid = generate_prepay_transaction(client_id, payer_id, payee_id, order, amount,
                                                   request.url_root, config.payment.notify_url)
    pay_url = _build_pay_url(transaction_uuid)

    return jsonify({'pay_url': pay_url})


@mod.route('/pay/<uuid>', methods=['GET'])
def pay(uuid):
    form_submit = pay_by_uuid(uuid)
    return Response(form_submit, status=200, mimetype='text/html')


@mod.route('/pay/<uuid>/result', methods=['POST'])
def notify_payment(uuid):
    request_values = request.values
    partner_oid = request_values['oid_partner']
    order_no = request_values['no_order']
    amount = Decimal(request_values['money_order'])
    pay_result = request_values['result_pay']
    paybill_oid = request_values['oid_paybill']

    if (not is_my_response(partner_oid)) or (not is_valid_transaction(order_no, uuid, amount)):
        return _mark_as_invalid_notification()

    if not is_successful_payment(pay_result):
        fail_transaction(order_no)
        return _mark_as_failure()

    succeed_transaction(order_no, paybill_oid)
    return _mark_as_success()


def _mark_as_notified():
    return jsonify({'ret_code': '0000', 'ret_msg': '重复通知'})


def _mark_as_success():
    return jsonify({'ret_code': '0000', 'ret_msg': '交易成功'})


def _mark_as_failure():
    return jsonify({'ret_code': '0000', 'ret_msg': '交易失败'})


def _mark_as_invalid_notification():
    return jsonify({'ret_code': '9999'})


def _build_pay_url(transaction_uuid):
    return urljoin(request.url_root, 'pay/{0}').format(transaction_uuid)
