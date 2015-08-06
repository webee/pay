# -*- coding: utf-8 -*-
from flask import Blueprint, request, Response

from api.guaranteed_pay.payment.prepay import *
from api.guaranteed_pay.payment.pay import pay_by_id, PaymentNotFoundError
from api.guaranteed_pay.payment.postpay import get_secured_payment
from api.guaranteed_pay.refund.refund import apply_to_refund
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
