# -*- coding: utf-8 -*-
from decimal import Decimal

from flask import Blueprint, request, redirect, Response
from api.account import get_account_by_user_info, get_account_by_id
from api.core import query_bankcard_bin, list_all_bankcards as _list_all_bankcards, add_bankcard as _add_bankcard, \
    ZytCoreError, apply_to_withdraw, list_unfailed_withdraw, get_withdraw_basic_info_by_id, get_cash_balance
from api.secured_transaction.payment.pay import pay_by_id, PaymentNotFoundError
from api.util import response
from api.util.parser import to_bool
from api.util.uuid import decode_uuid

mod = Blueprint('common_transaction', __name__)


@mod.route('/')
def index():
    return redirect('http://huodong.lvye.com')


@mod.route('/pay/<uuid>', methods=['GET'])
def pay(uuid):
    try:
        payment_id = decode_uuid(uuid)
        form_submit = pay_by_id(payment_id)
        return Response(form_submit, status=200, mimetype='text/html')
    except PaymentNotFoundError:
        return response.not_found({'uuid': uuid})


@mod.route('/user_domains/<int:user_domain_id>/users/<user_id>/account', methods=['GET'])
def get_account_info(user_domain_id, user_id):
    account = get_account_by_user_info(user_domain_id, user_id)
    if not account:
        return response.not_found({'user_domain_id': user_domain_id, 'user_id': user_id})

    account_id = account['id']
    return response.ok(account_id=account_id)


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


@mod.route('/accounts/<int:account_id>/balance', methods=['GET'])
def account_balance(account_id):
    account = get_account_by_id(account_id)
    if not account:
        return response.not_found()

    balance = get_cash_balance(account_id)
    return response.ok(balance=balance)


@mod.route('/accounts/<int:account_id>/withdraw', methods=['POST'])
def withdraw(account_id):
    data = request.values
    bankcard_id = data['bankcard_id']
    callback_url = data['callback_url']
    amount = Decimal(data['amount'])

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
def withdraw_detail(withdraw_id):
    withdraw_record = get_withdraw_basic_info_by_id(withdraw_id)
    if not withdraw_record:
        return response.not_found({'withdraw_id': withdraw_id})
    return response.ok(dict(withdraw_record))
