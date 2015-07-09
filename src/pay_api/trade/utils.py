# coding=utf-8

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
