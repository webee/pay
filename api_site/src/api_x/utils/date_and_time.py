# coding=utf-8
from datetime import datetime


def today():
    today = datetime.today()
    return datetime(today.year, today.month, today.day)


def utctoday():
    today, n, un = datetime.today(), datetime.now(), datetime.utcnow()
    return datetime(today.year, today.month, today.day) - (n - un)