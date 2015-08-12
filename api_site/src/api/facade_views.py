# -*- coding: utf-8 -*-
from decimal import Decimal

from flask import Blueprint, request, redirect, Response
from api.account import get_account_by_user_info, get_account_by_id, find_or_create_account
from api.core import query_bankcard_bin, list_all_bankcards as _list_all_bankcards, add_bankcard as _add_bankcard, \
    ZytCoreError, apply_to_withdraw, list_unfailed_withdraw, get_withdraw_basic_info_by_id, get_cash_balance, \
    transfer as core_transfer, list_cash_transaction_logs
from api.charged_withdraw import apply_to_charged_withdraw
from api import delegate
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
        form_submitted = delegate.pay(payment_id)
        return Response(form_submitted, status=200, mimetype='text/html')
    except IOError:
        return response.not_found({'uuid': uuid})


@mod.route('/user_domains/<int:user_domain_id>/users/<user_id>/account', methods=['GET'])
def get_account_id(user_domain_id, user_id):
    account = get_account_by_user_info(user_domain_id, user_id)
    if account:
        account_id = account['id']
    else:
        account_id = find_or_create_account(user_domain_id, user_id)

    return response.ok(account_id=account_id)


@mod.route('/accounts/<int:account_id>', methods=['GET'])
def get_account_info_by_id(account_id):
    account = get_account_by_id(account_id)
    if not account:
        return response.not_found()

    return response.ok(dict(account))


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


@mod.route('/accounts/<int:account_id>/charged-withdraw', methods=['POST'])
def withdraw(account_id):
    data = request.values
    bankcard_id = data['bankcard_id']
    amount = Decimal(data['amount'])
    charged_fee = Decimal(data['fee'])
    callback_url = data.get('callback_url', '')

    if charged_fee >= amount:
        response.bad_request('Charged fee of withdraw should be less than total amount', amount=amount, fee=charged_fee)

    charged_withdraw_id = apply_to_charged_withdraw(account_id, bankcard_id, amount, charged_fee, callback_url)
    return response.accepted(charged_withdraw_id)


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


@mod.route('/accounts/<int:from_account_id>/transfer/to/<int:to_account_id>', methods=['POST'])
def transfer(from_account_id, to_account_id):
    data = request.values
    from_account_id = int(from_account_id)
    order_no = data['order_no']
    order_info = data['order_info']
    amount = Decimal(data['amount'])

    try:
        _id = core_transfer(order_no, order_info, from_account_id, to_account_id, amount)
        return response.ok(transfer_id=_id)
    except ZytCoreError, e:
        return response.bad_request(e.message)


@mod.route('/accounts/<int:account_id>/cash_records', methods=['GET'])
def user_cash_records(account_id):
    q = request.args.get('q', '')
    side = request.args.get('side', '')
    tp = request.args.get('tp', '')
    page_no = int(request.args.get('page_no', 1))
    page_size = int(request.args.get('page_size', 20))
    count, cash_records, orders_info = list_cash_transaction_logs(account_id, q, side, tp, page_no, page_size)

    cash_records = [dict(cash_record) for cash_record in cash_records]
    orders_info = {order_id: dict(order) for order_id, order in orders_info.items()}

    return response.ok(count=count, page_no=page_no, page_size=page_size,
                       records=cash_records, record_infos=orders_info)