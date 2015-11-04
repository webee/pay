# coding=utf-8


class App:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://lvye_pay:p@55word@127.0.0.1:3306/lvye_pay'
    SQLALCHEMY_ECHO = True


class Biz:
    VALID_NETLOCS = ['test_pay.lvye.com:5100']


HOST_URL = 'http://test_pay.lvye.com:5100'
CHECKOUT_URL = 'http://dev_pay.lvye.com:5102/checkout/{sn}'

TEST_CHANNELS = {'zyt_sample'}
