# coding=utf-8
from datetime import datetime


def today():
    td = datetime.today()
    return datetime(td.year, td.month, td.day)


def utctoday():
    td, n, un = datetime.today(), datetime.now(), datetime.utcnow()
    return datetime(td.year, td.month, td.day) - (n - un)