# coding=utf-8
import os


class App:
    DEBUG = False
    TESTING = False

    # database
    SQLALCHEMY_DATABASE_URI = os.environ['PAY_API_SITE_DATABASE_URI']
    SQLALCHEMY_ECHO = False

HOST_URL = 'http://pay.lvye.com/api'


class Biz:
    TX_SN_PREFIX = ''
    IS_PROD = True

    ACTIVATED_EVAS = ['LIANLIAN_PAY', 'WEIXIN_PAY']
