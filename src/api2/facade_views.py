# -*- coding: utf-8 -*-
from flask import Blueprint, request, Response

from api2.account import get_account_by_user_info
from api2.core import query_bankcard_bin, list_all_bankcards as _list_all_bankcards
from api2.guaranteed_pay.payment.prepay import *
from api2.guaranteed_pay.payment.pay import pay_by_uuid, PaymentNotFoundError
from api2.guaranteed_pay.payment.confirm_pay import confirm_payment
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


@mod.route('/clients/<int:client_id>/users/<user_id>/account', methods=['GET'])
def get_account_info(client_id, user_id):
    account = get_account_by_user_info(client_id, user_id)
    if not account:
        return response.not_found({'client_id': client_id, 'user_id': user_id})

    account_id = account['id']
    return response.ok(account_id=account_id)


@mod.route('/clients/<int:client_id>/orders/<order_id>/confirm-pay', methods=['PUT'])
def confirm_to_pay(client_id, order_id):
    pay_record = find_payment_by_order_no(client_id, order_id)
    if not pay_record:
        return response.not_found({'client_id': client_id, 'order_id': order_id})

    payment_id = confirm_payment(client_id, pay_record)
    return response.ok(id=(payment_id or pay_record['id']))


@mod.route('/bankcards/<card_no>/bin', methods=['GET'])
def query_bin(card_no):
    card = query_bankcard_bin(card_no)
    if not card:
        return response.not_found({'card_no': card_no})
    return response.ok(card)


@mod.route('/accounts/<int:account_id>/bankcards', methods=['GET'])
def list_all_bankcards(account_id):
    bankcards = _list_all_bankcards(account_id)
    bankcards = [dict(bankcard) for bankcard in bankcards]
    return response.list_data(bankcards)