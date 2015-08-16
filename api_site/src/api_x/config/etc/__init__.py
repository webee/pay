# coding=utf-8


class App:
    import os

    SECRET_KEY = os.environ.get('SECRET_KEY') or '.yek eyvl'
    TESTING = False
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql://pay_system:p@55word@127.0.0.1:3306/pay_system'
    SQLALCHEMY_ECHO = False


HOST_URL = 'http://pay.lvye.com'
