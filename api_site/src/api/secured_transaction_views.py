# -*- coding: utf-8 -*-
from flask import Blueprint, request, Response

from api.secured_transaction.payment.prepay import *
from api.secured_transaction.payment.postpay import get_secured_payment
from api.secured_transaction.payment.confirm_pay import confirm_payment
from api.secured_transaction.refund.refund import apply_to_refund
from api.secured_transaction.payment.pay import pay_by_id, PaymentNotFoundError
from api.util import response
from api.util.uuid import decode_uuid


secured_mod = Blueprint('secured_transaction', __name__)
mod = secured_mod


@mod.route('/pre-pay', methods=['POST'])
def prepay():
    data = request.values
    channel_id = data['client_id']
    payer_id = data['payer']
    payee_id = data['payee']
    order = Order(data['activity_id'], data['order_no'], data['order_name'], data['order_desc'], data['ordered_on'])
    amount = data['amount']
    client_callback_url = data['client_callback_url']
    client_async_callback_url = data['client_async_callback_url']

    payment_id = find_or_create_prepay_transaction(channel_id, payer_id, payee_id, order,
                                                   amount, client_callback_url, client_async_callback_url)
    pay_url = generate_pay_url(payment_id)

    return response.ok(pay_url=pay_url)


@mod.route('/pay/<uuid>', methods=['GET'])
def pay(uuid):
    try:
        payment_id = decode_uuid(uuid)
        form_submit = pay_by_id(payment_id)
        return Response(form_submit, status=200, mimetype='text/html')
    except PaymentNotFoundError:
        return response.not_found({'uuid': uuid})


@mod.route('/clients/<int:client_id>/orders/<order_id>/confirm-pay', methods=['PUT'])
def confirm_to_pay(client_id, order_id):
    pay_record = find_payment_by_order_no(client_id, order_id)
    if not pay_record:
        return response.not_found({'client_id': client_id, 'order_id': order_id})

    payment_id = confirm_payment(pay_record)
    return response.ok(id=(payment_id or pay_record['id']))


@mod.route('/refund', methods=['POST'])
def apply_for_refund():
    data = request.values
    channel_id = data['client_id']
    order_no = data['order_no']
    amount = data['amount']
    callback_url = data['callback_url']

    pay_record = get_secured_payment(channel_id, order_no)
    if not pay_record:
        return response.not_found({'client_id': channel_id, 'order_no': order_no})

    refund_id = apply_to_refund(pay_record, amount, callback_url)
    return response.accepted(refund_id)
