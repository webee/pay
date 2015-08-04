# -*- coding: utf-8 -*-
from decimal import Decimal


def to_bool(text):
    return text is not None and text.lower() == 'true'


def to_int(n, default=0):
    try:
        return int(n)
    except:
        return default


def to_float(n, default=0):
    try:
        return float(n)
    except:
        return default


def to_decimal(float_price):
    return Decimal('%.2f' % float_price)