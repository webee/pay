# coding=utf-8
import decimal
import string
import random


def format_string(text):
    return "" if not text else text.strip()


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
    return decimal.Decimal('%.2f' % float_price)


def str_generator(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
