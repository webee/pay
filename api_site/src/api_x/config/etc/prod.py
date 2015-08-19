# coding=utf-8
import os


class App:
    DEBUG = False
    TESTING = False

    # database
    SQLALCHEMY_DATABASE_URI = os.environ['PAY_API_SITE_DATABASE_URI']
    SQLALCHEMY_ECHO = False

HOST_URL = 'http://pay.lvye.com/api'
