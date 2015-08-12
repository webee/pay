# -*- coding: utf-8 -*-
from datetime import datetime


def charged_withdraw_id(account_id):
    return _generate(account_id, 'CGW')


def _generate(account_id, prefix):
    return prefix + datetime.now().strftime("%Y%m%d%H%M%S%f") + '%0.7d' % account_id
