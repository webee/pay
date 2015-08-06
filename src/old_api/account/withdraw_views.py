# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import request

from . import account_mod as mod
from old_api.account.error import NoBankcardFoundError, InsufficientBalanceError
from old_api.util.error import AmountError
from .withdraw.error import WithdrawError, WithdrawRequestFailedError
from . import withdraw
from old_api.util import response
from old_api.util.ipay.transaction import notification
from old_api.util.ipay.transaction import parse_and_verify, is_valid_transaction
from tools.mylog import get_logger

logger = get_logger(__name__)


@mod.route('/<int:account_id>/withdraw', methods=['POST'])
def apply_for_withdraw(account_id):
    req_data = request.values
    bankcard_id = req_data.get('bankcard_id')
    callback_url = req_data.get('callback_url')
    amount = req_data.get('amount')

    try:
        order_id = withdraw.apply_for_withdraw(account_id, bankcard_id, amount, callback_url)
        return response.accepted(order_id)
    except NoBankcardFoundError as e:
        return response.bad_request(e.message)
    except AmountError as e:
        return response.bad_request(e.message)
    except InsufficientBalanceError as e:
        return response.bad_request(e.message)
    except WithdrawRequestFailedError as e:
        return response.bad_request(e.message, withraw_id=e.withdraw_id)
    except WithdrawError as e:
        return response.bad_request(e.message)
    except Exception as e:
        return response.bad_request(e.message)


@mod.route('/<int:account_id>/withdraw/<uuid>/notify', methods=['POST'])
@parse_and_verify
def notify_withdraw(account_id, uuid):
    data = request.verified_data

    oid_partner = data['oid_partner']
    withdraw_id = data['no_order']
    if not is_valid_transaction(oid_partner, withdraw_id, uuid):
        return notification.is_invalid()

    return withdraw.handle_withdraw_notify(account_id, withdraw_id, data)


@mod.route('/<int:account_id>/withdraw', methods=['GET'])
def list_withdraw(account_id):
    withdraw_list = withdraw.list_unfailed_withdraw(account_id)
    return response.list_data(withdraw_list)


@mod.route('/<int:account_id>/withdraw/<withdraw_id>', methods=['GET'])
def withdraw_detail(account_id, withdraw_id):
    withdraw_record = withdraw.get_withdraw_by_id(withdraw_id)
    if not withdraw_record:
        return response.not_found({'account_id': account_id, 'withdraw_id': withdraw_id})
    return response.ok(dict(withdraw_record))
