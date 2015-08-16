t # -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import url_for, Response
from .lianlian.pay import pay as _pay
from api_x.config import lianlian_pay


NAME = 'LIANLIAN_PAY'


def pay(source, user_id, user_created_on, ip, order_no, order_name, order_desc, amount):
    return_url = lianlian_pay.ROOT_URL + url_for('lianlian_pay_entry.pay_result', pay_source=source)
    notify_url = lianlian_pay.ROOT_URL + url_for('lianlian_pay_entry.pay_notify', pay_source=source)

    return Response(_pay(user_id, user_created_on, ip, order_no, order_name, order_desc, amount,
                         return_url, notify_url))


def refund():
    pass


def pay_to_bankcard():
    pass


def query_bin():
    pass


def is_sending_to_me(partner_id):
    return partner_id == lianlian_pay.OID_PARTNER
