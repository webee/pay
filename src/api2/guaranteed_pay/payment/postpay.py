# -*- coding: utf-8 -*-
from .dba import find_payment_by_id
from api2.account import get_account_by_id


def get_sync_callback_url_of_payment(pay_record_id):
    pay_record = find_payment_by_id(pay_record_id)
    callback_url = pay_record['client_callback_url']

    payer_account = get_account_by_id(pay_record['payer_account_id'])

    return '{0}?user_id={1}&order_id={2}&amount={3}&status=money_locked'.\
        format(callback_url, payer_account['user_id'], pay_record['order_id'], pay_record['amount'])
