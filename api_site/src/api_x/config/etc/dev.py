# coding=utf-8


class App:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://lvye_pay:p@55word@127.0.0.1:3306/lvye_pay'
    SQLALCHEMY_ECHO = False


class Biz:
    VALID_NETLOCS = ['localhost:5100', 'dev_pay.lvye.com:5100']


HOST_URL = 'http://localhost:5100'


TEST_CHANNELS = {'zyt_sample', 'lvye_pay_test'}
