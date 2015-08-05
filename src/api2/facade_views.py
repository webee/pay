# -*- coding: utf-8 -*-
from flask import Blueprint, request, redirect, Response

from api2.account import get_account_by_user_info
from api2.core import query_bankcard_bin, list_all_bankcards as _list_all_bankcards, add_bankcard as _add_bankcard, \
    ZytCoreError, apply_to_withdraw, list_unfailed_withdraw, get_withdraw_basic_info_by_id
from api2.guaranteed_pay.payment.prepay import *
from api2.guaranteed_pay.payment.pay import pay_by_id, PaymentNotFoundError
from api2.guaranteed_pay.payment.confirm_pay import confirm_payment
from api2.guaranteed_pay.payment.postpay import get_secured_payment
from api2.guaranteed_pay.refund.refund import apply_to_refund
from api2.util import response
from api2.util.parser import to_bool
from api2.util.uuid import decode_uuid

mod = Blueprint('api', __name__)


@mod.route('/')
def index():
    return redirect('http://huodong.lvye.com')


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

    payment_id = confirm_payment(pay_record)
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


@mod.route('/accounts/<int:account_id>/bankcards', methods=['POST'])
def add_bankcard(account_id):
    data = request.values
    card_no = data['card_no']
    account_name = data['account_name']
    is_corporate_account = to_bool(data['is_corporate_account'])
    province_code = data['province_code']
    city_code = data['city_code']
    branch_bank_name = data['branch_bank_name']

    try:
        bankcard_id = _add_bankcard(account_id, card_no, account_name, is_corporate_account, province_code, city_code,
                                    branch_bank_name)
        return response.created(bankcard_id)
    except ZytCoreError, e:
        return response.bad_request(e.message, card_no=card_no)


@mod.route('/accounts/<int:account_id>/withdraw', methods=['POST'])
def withdraw(account_id):
    req_data = request.values
    bankcard_id = req_data.get('bankcard_id')
    callback_url = req_data.get('callback_url')
    amount = req_data.get('amount')

    try:
        order_id = apply_to_withdraw(account_id, bankcard_id, amount, callback_url)
        return response.accepted(order_id)
    except ZytCoreError, e:
        return response.bad_request(e.message)


@mod.route('/accounts/<int:account_id>/withdraw', methods=['GET'])
def list_withdraw(account_id):
    withdraw_list = list_unfailed_withdraw(account_id)
    return response.list_data(withdraw_list)


@mod.route('/withdraw/<withdraw_id>', methods=['GET'])
def withdraw_detail(account_id, withdraw_id):
    withdraw_record = get_withdraw_basic_info_by_id(withdraw_id)
    if not withdraw_record:
        return response.not_found({'account_id': account_id, 'withdraw_id': withdraw_id})
    return response.ok(dict(withdraw_record))


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
