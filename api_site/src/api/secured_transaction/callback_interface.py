# -*- coding: utf-8 -*-
from .payment.pay import pay_by_id as _pay_by_id
from .payment.postpay import get_sync_callback_url_of_payment as _get_sync_callback_url_of_payment, \
    guarantee_payment as _guarantee_payment


def get_sync_callback_url_of_payment(pay_record_id):
    return _get_sync_callback_url_of_payment(pay_record_id)


def guarantee_payment(pay_record_id):
    return _guarantee_payment(pay_record_id)


def pay_by_id(pay_record_id):
    return _pay_by_id(pay_record_id)
