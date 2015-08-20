# coding=utf-8


class App:
    import os

    JSON_AS_ASCII = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or '.yek eyvl'
    TESTING = False
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql://lvye_pay:p@55word@127.0.0.1:3306/lvye_pay'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_SIZE = 30
    SQLALCHEMY_POOL_TIMEOUT = 60
    SQLALCHEMY_MAX_OVERFLOW = 60
    SQLALCHEMY_POOL_RECYCLE = 3600


HOST_URL = 'http://pay.lvye.com/api'
