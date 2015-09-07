# coding=utf-8
from __future__ import unicode_literals
from flask import request
import re
from api_x.constant import RequestClientType


def ip():
    # FIXME
    x_real_ip = request.headers.environ.get('X-Real-Ip')
    x_forwarded_for = request.headers.environ.get('X-Forwarded-For')

    _ip = x_real_ip or x_forwarded_for or request.remote_addr or "61.148.57.6"
    if _ip.startswith('192.168'):
        _ip = "61.148.57.6"
    return _ip


MOBILE_PT = re.compile(r'Mobile|iP(hone|od|ad)|Android|BlackBerry|IEMobile|Kindle|NetFront|Silk-Accelerated|(hpw|web)OS|Fennec|Minimo|Opera M(obi|ini)|Blazer|Dolfin|Dolphin|Skyfire|Zune')
IOS_PT = re.compile(r'iphone|ipad', flags=re.IGNORECASE)
ANDROID_PT = re.compile(r'android', flags=re.IGNORECASE)


def client_type():
    user_agent = request.user_agent.string

    if MOBILE_PT.search(user_agent):
        # is mobile
        if IOS_PT.search(user_agent):
            return RequestClientType.IOS
        if ANDROID_PT.search(user_agent):
            return RequestClientType.ANDROID
        return RequestClientType.WAP

    return RequestClientType.WEB
