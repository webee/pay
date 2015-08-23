# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import url_for, Response
from .commons import generate_absolute_url
from pytoolbox.util.sign import Signer


NAME = 'LIANLIAN_PAY'

signer = Signer('key', 'sign')


def pay(source, user_id, user_created_on, ip, order_no, ordered_on, order_name, order_desc, amount):
    from .pay import pay as _pay

    return_url = generate_absolute_url(url_for('lianlian_pay_entry.pay_result', source=source))
    notify_url = generate_absolute_url(url_for('lianlian_pay_entry.pay_notify', source=source))

    return Response(_pay(user_id, user_created_on, ip, order_no, ordered_on, order_name, order_desc, amount,
                         return_url, notify_url))


def refund(source, refund_no, refunded_on, amount, paybill_id):
    from .refund import refund as _refund

    notify_url = generate_absolute_url(url_for('lianlian_pay_entry.refund_notify', source=source))
    return _refund(refund_no, refunded_on, amount, paybill_id, notify_url)


def pay_to_bankcard(source, no_order, money_order, info_order,
                    flag_card, card_type, card_no, acct_name,
                    bank_code='', province_code='', city_code='', brabank_name='',
                    prcptcd=''):
    from .pay_to_bankcard import pay_to_bankcard as _pay_to_bankcard

    notify_url = generate_absolute_url(url_for('lianlian_pay_entry.pay_to_bankcard_notify', source=source))
    return _pay_to_bankcard(no_order, money_order, info_order, notify_url,
                            flag_card, card_type, card_no, acct_name,
                            bank_code, province_code, city_code, brabank_name, prcptcd)


def query_bin(card_no):
    from .bankcard import query_bin as _query_bin

    return _query_bin(card_no)
