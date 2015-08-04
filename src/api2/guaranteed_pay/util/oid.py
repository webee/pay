# -*- coding: utf-8 -*-
from datetime import datetime


def pay_id(account_id):
    return _generate(account_id, 'PAY')


def secured_pay_id(account_id):
    return _generate(account_id, 'SCP')


def confirmed_pay_id(account_id):
    return _generate(account_id, 'CFP')


def withdraw_id(account_id):
    return _generate(account_id, 'WDR')


def refund_id(account_id):
    return _generate(account_id, 'RFD')


def _generate(account_id, prefix):
    return prefix + datetime.now().strftime("%Y%m%d%H%M%S%f") + '%0.7d' % account_id