# coding=utf-8


class App:
    import os

    SECRET_KEY = os.environ.get('SECRET_KEY') or '.yek eyvl'
    TESTING = False
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql://lvye_pay:p@55word@localhost:3306/lvye_pay'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_SIZE = 30
    SQLALCHEMY_POOL_TIMEOUT = 60
    SQLALCHEMY_MAX_OVERFLOW = 60
    SQLALCHEMY_POOL_RECYCLE = 3600


HOST_URL = 'http://pay.lvye.com/api'
