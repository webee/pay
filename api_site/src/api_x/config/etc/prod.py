# coding=utf-8
import os


class App:
    DEBUG = False
    TESTING = False

    # database
    SQLALCHEMY_DATABASE_URI = os.environ['PAY_API_SITE_DATABASE_URI']
    SQLALCHEMY_ECHO = False

    ENTRY_PREFIX = ''

HOST_URL = 'http://pay.lvye.com/api'


class Biz:
    TX_SN_PREFIX = ''

    ACTIVATED_EVAS = ['LIANLIAN_PAY']
