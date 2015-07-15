# -*- coding: utf-8 -*-
from datetime import datetime


def generate(account_id):
    return datetime.now().strftime("%Y%m%d%H%M%S%f") + '%0.7d' % account_id