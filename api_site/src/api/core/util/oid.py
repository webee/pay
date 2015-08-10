# -*- coding: utf-8 -*-
from datetime import datetime


def pay_id(account_id):
    return _generate(account_id, 'PAY')


def withdraw_id(account_id):
    return _generate(account_id, 'WDR')


def refund_id(account_id):
    return _generate(account_id, 'RFD')


def transfer_id(account_id):
    return _generate(account_id, 'TFR')


def prepaid_id(account_id):
    return _generate(account_id, 'PRP')


def _generate(account_id, prefix):
    return prefix + datetime.now().strftime("%Y%m%d%H%M%S%f") + '%0.7d' % account_id
