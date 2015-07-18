# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

from . import refund_mod as mod
from .refund import refund_transaction, NoTransactionFoundError, RefundFailedError
from flask import jsonify, request, abort

log = logging.getLogger(__name__)


@mod.route('/refund', methods=['POST'])
def refund():
    data = request.values
    client_id = data['client_id']
    payer_id = data['payer']
    order_no = data['order_no']
    amount = data['amount']

    try:
        refund_id = refund_transaction(client_id, payer_id, order_no, amount, request.url_root)
        return _response_accepted(refund_id)
    except NoTransactionFoundError:
        return abort(404)
    except RefundFailedError, e:
        return _response_created(e.refund_id)


@mod.route('/refund/<uuid>/result', methods=['POST'])
def notify_refund_result(uuid):
    return jsonify({})


@mod.route('/client/<client_id>/order/<order_no>/refund', methods=['GET'])
def query_refund_result(client_id, order_no):
    return jsonify({})


def _response_accepted(refund_id):
    return _response_with_code(refund_id, 202)


def _response_created(refund_id):
    return _response_with_code(refund_id, 201)


def _response_with_code(refund_id, status_code):
    response = jsonify({'refund_id': refund_id})
    response.status_code = status_code
    return response
