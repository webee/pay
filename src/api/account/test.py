# coding=utf-8
from __future__ import unicode_literals, print_function
from datetime import datetime


def get_current_datetime_str():
    now = datetime.now()
    return now.strftime('%Y%m%d%H%M%S%f')

