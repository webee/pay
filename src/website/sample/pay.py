# -*- coding: utf-8 -*-
from datetime import datetime
import requests


def pay(amount):
    order_no = _generate_order_id()
    params = {
        'client_id': 1,
        'payer': 2001,
        'payee': 1001,
        'order_no': order_no,
        'order_name': 'Christmas gift',
        'order_desc': 'Gift to my friend',
        'ordered_on': datetime(2015, 6, 19, 18, 28, 35),
        'amount': amount,
        'client_callback_url': 'http://localhost:5001/site/sample/pay/{0}/notify-result'.format(order_no)
    }
    return requests.post('http://localhost:5000/pre-pay', data=params)


def _generate_order_id():
    return datetime.now().strftime("%Y%m%d%H%M%S%f")
