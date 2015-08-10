# -*- coding: utf-8 -*-
from flask import Blueprint, request

from api.util import response
from api.direct_transaction.payment import Order, find_or_create_pay_transaction, generate_pay_url


direct_mod = Blueprint('direct_transaction', __name__)
mod = direct_mod


@mod.route('/pre-pay', methods=['POST'])
def pay():
    data = request.values
    channel_id = data['client_id']
    payer_id = data['payer']
    payee_id = data['payee']
    order = Order(data['order_no'], data['order_name'], data['order_desc'], data['ordered_on'])
    amount = data['amount']
    client_callback_url = data.get('client_callback_url', '')
    client_async_callback_url = data.get('client_async_callback_url', '')

    payment_id = find_or_create_pay_transaction(channel_id, payer_id, payee_id, order,
                                                   amount, client_callback_url, client_async_callback_url)

    pay_url = generate_pay_url(payment_id)
    return response.ok(pay_url=pay_url)
