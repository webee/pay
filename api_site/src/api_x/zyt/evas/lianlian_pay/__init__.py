# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import url_for, Response
from .commons import generate_absolute_url
from .pay import pay as _pay


NAME = 'LIANLIAN_PAY'


def pay(source, user_id, user_created_on, ip, order_no, ordered_on, order_name, order_desc, amount):
    return_url = generate_absolute_url(url_for('lianlian_pay_entry.pay_result', pay_source=source))
    notify_url = generate_absolute_url(url_for('lianlian_pay_entry.pay_notify', pay_source=source))

    return Response(_pay(user_id, user_created_on, ip, order_no, ordered_on, order_name, order_desc, amount,
                         return_url, notify_url))


def refund():
    pass


def pay_to_bankcard():
    pass


def query_bin():
    pass
