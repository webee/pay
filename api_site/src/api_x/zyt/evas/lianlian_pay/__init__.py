# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import url_for, Response
from .commons import generate_absolute_url
from .pay import pay as _pay
from .refund import refund as _refund


NAME = 'LIANLIAN_PAY'


def pay(source, user_id, user_created_on, ip, order_no, ordered_on, order_name, order_desc, amount):
    return_url = generate_absolute_url(url_for('lianlian_pay_entry.pay_result', pay_source=source))
    notify_url = generate_absolute_url(url_for('lianlian_pay_entry.pay_notify', pay_source=source))

    return Response(_pay(user_id, user_created_on, ip, order_no, ordered_on, order_name, order_desc, amount,
                         return_url, notify_url))


def refund(source, refund_no, refunded_on, amount, paybill_id):
    notify_url = generate_absolute_url(url_for('lianlian_pay_entry.refund_notify', refund_source=source))
    return _refund(refund_no, refunded_on, amount, paybill_id, notify_url)


def pay_to_bankcard():
    pass


def query_bin():
    pass
