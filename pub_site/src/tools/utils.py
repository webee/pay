# coding=utf-8
import decimal


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


def to_bankcard_mask(value):
    return u"%s **** **** %s" % (value[:4], value[-4:])
