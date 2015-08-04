# -*- coding: utf-8 -*-
from decimal import Decimal
from flask import Blueprint, request, redirect

from api2.core.postpay import *
from api2.core.ipay.transaction import parse_and_verify, notification, is_sending_to_me
from api2.guaranteed_pay.payment.postpay import get_sync_callback_url_of_payment, guarantee_payment
from api2.util.enum import enum

core_mod = Blueprint('api', __name__)
mod = core_mod


PayResult = enum(Success=0, Failure=1, IsInvalidRequest=2)


@mod.route('/pay/<uuid>/result', methods=['POST'])
@parse_and_verify
def receive_pay_result(uuid):
    result = _notify_payment_result(uuid, request.verified_data)

    if result == PayResult.IsInvalidRequest:
        return notification.is_invalid
    elif result == PayResult.Failure:
        return notification.fail
    else:
        pay_record = find_payment_by_uuid(uuid)
        return _redirect_pay_result(pay_record)


@mod.route('/pay/<uuid>/notify', methods=['POST'])
@parse_and_verify
def notify_payment(uuid):
    result = _notify_payment_result(uuid, request.verified_data)
    if result == PayResult.IsInvalidRequest:
        return notification.is_invalid()
    elif result == PayResult.Failure:
        return notification.fail()
    else:
        return notification.succeed()


def _notify_payment_result(uuid, data):
    partner_oid = data['oid_partner']
    order_no = data['no_order']
    amount = Decimal(data['money_order'])
    pay_result = data['result_pay']
    paybill_oid = data['oid_paybill']

    if (not is_sending_to_me(partner_oid)) or (not is_valid_payment(order_no, uuid, amount)):
        return PayResult.IsInvalidRequest

    if not is_successful_payment(pay_result):
        fail_payment(order_no)
        return PayResult.Failure

    pay_record = succeed_payment(order_no, paybill_oid)
    guarantee_payment(pay_record['trade_id'])
    return PayResult.Success


def _redirect_pay_result(pay_record):
    return redirect(get_sync_callback_url_of_payment(pay_record['trade_id']))
