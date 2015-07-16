# -*- coding: utf-8 -*-
from datetime import datetime


def generate(account_id, prefix='LLP'):
    return prefix[:3] + datetime.now().strftime("%Y%m%d%H%M%S%f") + '%0.7d' % account_id