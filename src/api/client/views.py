# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

from . import client_mod as mod
from api.account.account.dba import get_account
from api.payment.dba import find_payment_by_order_no
from api.payment.confirm_pay import confirm_payment
from api.util import response


log = logging.getLogger(__name__)


@mod.route('/<int:client_id>/users/<user_id>/account', methods=['GET'])
def get_account_info(client_id, user_id):
    account = get_account(client_id, user_id)
    if not account:
        return response.not_found({'client_id': client_id, 'user_id': user_id})

    account_id = account['id']
    return response.ok(account_id=account_id)


@mod.route('/<int:client_id>/orders/<order_id>/confirm-pay', methods=['POST'])
def confirm_to_pay(client_id, order_id):
    pay_record = find_payment_by_order_no(client_id, order_id)
    if not pay_record:
        return response.not_found({'client_id': client_id, 'order_id': order_id})

    payment_id = confirm_payment(pay_record)
    return response.ok(id=payment_id)
