# -*- coding: utf-8 -*-
import requests

from .payment import find_by_orderno


def refund(order_no):
    pay_record = find_by_orderno(order_no)
    params = {
        'client_id': pay_record['client_id'],
        'payer': pay_record['payer_account_id'],
        'order_no': order_no,
        'amount': pay_record['amount']
    }
    return requests.post('http://localhost:5000/refund', data=params)
