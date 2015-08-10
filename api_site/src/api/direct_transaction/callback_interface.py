# -*- coding: utf-8 -*-
from .payment import update_payment_to_be_success as _update_payment_to_be_success, \
    get_sync_callback_url_of_payment as _get_sync_callback_url_of_payment, pay_by_id as _pay_by_id

def update_payment_to_be_success(pay_record_id):
    return _update_payment_to_be_success(pay_record_id)


def get_sync_callback_url_of_payment(pay_record_id):
    return _get_sync_callback_url_of_payment(pay_record_id)


def pay_by_id(pay_record_id):
    return _pay_by_id(pay_record_id)
