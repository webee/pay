# coding=utf-8
import os


class App:
    DEBUG = False
    TESTING = False

    # database
    SQLALCHEMY_DATABASE_URI = 'mysql://lvye_pay:{0}@{1}:3306/lvye_pay'.format(
        os.environ['PAY_API_SITE_DATABASE_PASSWORD'], os.environ['PAY_API_SITE_DATABASE_HOST'])
    SQLALCHEMY_ECHO = False

HOST_URL = 'http://pay.lvye.com'
