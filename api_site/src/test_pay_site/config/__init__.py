# coding=utf-8
from __future__ import unicode_literals


class App:
    import os

    SECRET_KEY = os.environ.get('SECRET_KEY') or '.yek eyvl'
    TESTING = False
    DEBUG = True


MERCHANTS_TABLE = {
    '00001': u'webee测试商户'
}
