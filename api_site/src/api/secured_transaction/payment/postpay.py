# -*- coding: utf-8 -*-
from ._dba import find_payment_by_id, update_payment_state, PAYMENT_STATE, find_payment_by_order_no, request_secured_payment
from api.account import get_account_by_id


def guarantee_payment(pay_record_id):
    pay_record = find_payment_by_id(pay_record_id)
    request_secured_payment(pay_record_id, pay_record['payer_account_id'], pay_record['amount'])
    update_payment_state(pay_record_id, PAYMENT_STATE.SECURED)


def get_sync_callback_url_of_payment(pay_record_id):
    pay_record = find_payment_by_id(pay_record_id)
    callback_url = pay_record['client_callback_url']

    payer_account = get_account_by_id(pay_record['payer_account_id'])

    return '{0}?user_id={1}&order_id={2}&amount={3}&status=money_locked'.\
        format(callback_url, payer_account['user_id'], pay_record['order_id'], pay_record['amount'])


def get_secured_payment(channel_id, order_id):
    pay_record = find_payment_by_order_no(channel_id, order_id)
    if not pay_record:
        return None
    if pay_record['state'] != PAYMENT_STATE.SECURED:
        return None
    return pay_record


def mark_payment_as_refunding(pay_record_id):
    update_payment_state(pay_record_id, PAYMENT_STATE.REFUNDING)


def mark_payment_as_refunded(pay_record_id):
    update_payment_state(pay_record_id, PAYMENT_STATE.REFUNDED)

