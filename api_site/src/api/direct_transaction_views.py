# -*- coding: utf-8 -*-
from flask import Blueprint, request, Response
from api.direct_transaction.payment import Order, find_or_create_pay_transaction, pay_by_id

direct_mod = Blueprint('direct_transaction', __name__)
mod = direct_mod


@mod.route('/pay', methods=['POST'])
def pay():
    data = request.values
    channel_id = data['client_id']
    payer_id = data['payer']
    payee_id = data['payee']
    order = Order(data['activity_id'], data['order_no'], data['order_name'], data['order_desc'], data['ordered_on'])
    amount = data['amount']
    client_callback_url = data['client_callback_url']
    client_async_callback_url = data['client_async_callback_url']

    payment_id = find_or_create_pay_transaction(channel_id, payer_id, payee_id, order,
                                                   amount, client_callback_url, client_async_callback_url)
    form_submit = pay_by_id(payment_id)
    return Response(form_submit, status=200, mimetype='text/html')

