# -*- coding: utf-8 -*-
from decimal import Decimal

from flask import Blueprint, request, redirect
from api.delegation_center import delegate
from api.core.postpay import *
from api.core.refund import get_refund_by_id, handle_refund_notification
from api.core.withdraw import get_withdraw_by_id, handle_withdraw_notification
from api.core.ipay.transaction import parse_and_verify, notification, is_sending_to_me, is_valid_transaction
from pytoolbox.util.enum import enum

core_mod = Blueprint('core_callback_response', __name__)
mod = core_mod

PayResult = enum(Success=0, Failure=1, IsInvalidRequest=2)



@mod.route('/pay/heart-beat')
def heart_beat_responser():
    return 'ok'


@mod.route('/pay/<uuid>/result', methods=['POST'])
@parse_and_verify
def receive_pay_result(uuid):
    result = _notify_payment_result(uuid, request.verified_data)

    if result == PayResult.IsInvalidRequest:
        return notification.is_invalid()
    elif result == PayResult.Failure:
        return notification.fail()
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


@mod.route('/withdraw/<uuid>/notify', methods=['POST'])
@parse_and_verify
def notify_withdraw(uuid):
    data = request.verified_data
    oid_partner = data['oid_partner']
    withdraw_id = data['no_order']
    amount = Decimal(data['money_order'])
    paybill_id = data['oid_paybill']
    result = data['result_pay']
    failure_info = data.get('info_order', '')

    if not is_valid_transaction(oid_partner, withdraw_id, uuid):
        return notification.is_invalid()

    withdraw_order = get_withdraw_by_id(withdraw_id)
    if not withdraw_order or withdraw_order.amount != amount:
        return notification.is_invalid()
    elif withdraw_order.state != 'FROZEN':
        return notification.duplicate()

    return handle_withdraw_notification(withdraw_id, paybill_id, result, failure_info)


@mod.route('/refund/<uuid>/notify', methods=['POST'])
@parse_and_verify
def notify_refund(uuid):
    data = request.verified_data
    oid_partner = data['oid_partner']
    refund_id = data['no_refund']
    amount = Decimal(data['money_refund'])
    sta_refund = data['sta_refund']
    oid_refundno = data['oid_refundno']

    if not is_valid_transaction(oid_partner, refund_id, uuid):
        return notification.is_invalid()

    refund_order = get_refund_by_id(refund_id)
    if not refund_order or refund_order.amount != amount:
        return notification.is_invalid()
    elif refund_order.state != 'CREATED':
        return notification.duplicate()

    return handle_refund_notification(refund_order, oid_refundno, sta_refund)


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
    delegate.paid(pay_record['trade_id'])
    return PayResult.Success


def _redirect_pay_result(pay_record):
    return redirect(delegate.redirect_web_after_paid(pay_record['trade_id']))

