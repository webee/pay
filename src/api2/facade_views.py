# -*- coding: utf-8 -*-
from flask import Blueprint, request, Response

from api2.account import get_account_by_user_info
from api2.guaranteed_pay.payment.prepay import *
from api2.guaranteed_pay.payment.pay import pay_by_uuid, PaymentNotFoundError
from api2.util import response

mod = Blueprint('api', __name__)


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

    return response.ok(pay_url=pay_url)


@mod.route('/pay/<uuid>', methods=['GET'])
def pay(uuid):
    try:
        form_submit = pay_by_uuid(uuid)
        return Response(form_submit, status=200, mimetype='text/html')
    except PaymentNotFoundError:
        return response.not_found({'uuid': uuid})


@mod.route('/accounts/<int:client_id>/users/<user_id>/account', methods=['GET'])
def get_account_info(client_id, user_id):
    account = get_account_by_user_info(client_id, user_id)
    if not account:
        return response.not_found({'client_id': client_id, 'user_id': user_id})

    account_id = account['id']
    return response.ok(account_id=account_id)
