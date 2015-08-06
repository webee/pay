# coding=utf-8
from __future__ import unicode_literals
from flask import request


def ip():
    x_real_ip = request.headers.environ.get('X-Real-Ip')
    x_forwarded_for = request.headers.environ.get('X-Forwarded-For')

    ip = x_real_ip or x_forwarded_for or request.remote_addr
    if not ip or ip.startswith('192.168'):
        ip = "61.148.57.6"
    return ip
