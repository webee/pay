# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

from . import refund_mod as mod
from api.util.error import AmountError
from api.util import response
from api.util.ipay.transaction import notification, parse_and_verify, is_valid_transaction
from flask import request
from api.refund.error import NoPaymentFoundError, PaymentStateMissMatchError, RefundError
from . import refund

log = logging.getLogger(__name__)


@mod.route('/prepare', methods=['POST'])
def prepare():
    data = request.values
    client_id = data['client_id']
    order_no = data['order_no']

    try:
        refund.prepare(client_id, order_no)
        return response.ok()
    except RefundError as e:
        return response.bad_request(e.message)
    except Exception as e:
        return response.bad_request(e.message)


@mod.route('/cancel', methods=['POST'])
def cancel():
    data = request.values
    client_id = data['client_id']
    order_no = data['order_no']

    try:
        refund.cancel(client_id, order_no)
        return response.ok()
    except RefundError as e:
        return response.bad_request(e.message)
    except Exception as e:
        return response.bad_request(e.message)


@mod.route('/', methods=['POST'])
def apply_for_refund():
    data = request.values
    client_id = data['client_id']
    order_no = data['order_no']
    amount = data['amount']
    callback_url = data['callback_url']

    try:
        refund_id = refund.apply_for_refund(client_id, order_no, amount, callback_url)
        return response.accepted(refund_id)
    except (NoPaymentFoundError, PaymentStateMissMatchError) as e:
        log.warn(e.message)
        return response.not_found()
    except AmountError as e:
        log.warn(e.message)
        return response.bad_request(e.message)
    except RefundError as e:
        return response.bad_request(e.message)
    except Exception as e:
        return response.bad_request(e.message)


@mod.route('/<uuid>/notify', methods=['POST'])
@parse_and_verify
def notify_refund(uuid):
    data = request.verified_data
    oid_partner = data['oid_partner']
    refund_id = data['no_refund']

    if not is_valid_transaction(oid_partner, refund_id, uuid):
        return notification.is_invalid()

    return refund.handle_refund_notify(refund_id, data)


@mod.route('/<refund_id>/query', methods=['GET'])
def query_refund(refund_id):
    refund_order = refund.query_refund(refund_id)
    if refund_order is None:
        return response.not_found({'refund_id': refund_id})
    return response.ok({k: v for k, v in refund_order.items()})


@mod.route('/query', methods=['POST'])
def query_refund_by_order_no():
    data = request.values
    client_id = data['client_id']
    order_no = data['order_no']

    #TODO
