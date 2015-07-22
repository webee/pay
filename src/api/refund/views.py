# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

from . import refund_mod as mod
from .refund import *
from api.util import response
from api.util.ipay.transaction import is_sending_to_me, notification, parse_and_verify
from flask import jsonify, request
from tools.utils import to_float

log = logging.getLogger(__name__)


@mod.route('/refund', methods=['POST'])
def refund():
    data = request.values
    client_id = data['client_id']
    payer_id = data['payer']
    order_no = data['order_no']
    amount = to_float(data['amount'])

    try:
        refund_id = refund_transaction(client_id, payer_id, order_no, amount)
        return response.accepted(refund_id)
    except NoPaymentFoundError:
        return response.not_found()
    except RefundFailedError, e:
        return response.created(e.refund_id)


@mod.route('/refund/<uuid>/result', methods=['POST'])
@parse_and_verify
def notify_refund_result(uuid):
    data = request.verified_data
    partner_oid = data['oid_partner']
    refund_id = data['no_refund']
    amount = data['money_refund']
    refund_result = data['sta_refund']
    refund_serial_no = data['oid_refundno']

    if (not is_sending_to_me(partner_oid)) or (not is_valid_refund(refund_id, uuid, amount)):
        return notification.is_invalid()

    if not is_successful_refund(refund_result):
        fail_refund(refund_id, refund_serial_no)
        return notification.fail()

    succeed_refund(refund_id, refund_serial_no)
    return notification.succeed()


@mod.route('/client/<client_id>/order/<order_no>/refund', methods=['GET'])
def query_refund_result(client_id, order_no):
    return jsonify({})
