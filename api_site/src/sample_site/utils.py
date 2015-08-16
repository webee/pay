# coding=utf-8
from __future__ import unicode_literals


def generate_order_id():
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d%H%M%S%f")