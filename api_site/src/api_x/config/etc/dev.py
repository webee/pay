# coding=utf-8


class App:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://lvye_pay:p@55word@127.0.0.1:3306/lvye_pay'
    SQLALCHEMY_ECHO = False


class Biz:
    ACTIVATED_EVAS = ['TEST_PAY', 'LIANLIAN_PAY', 'WEIXIN_PAY']
    VALID_NETLOCS = ['dev_pay.lvye.com:5100']

    PAYMENT_MAX_TRIAL_TIMES = 4
    PAYMENT_MAX_VALID_SECONDS = 600
    PAYMENT_CHECKOUT_VALID_SECONDS = 300


HOST_URL = 'http://dev_pay.lvye.com:5100'
CHECKOUT_URL = 'http://dev_pay.lvye.com:5102/checkout/{sn}'


TEST_CHANNELS = {'zyt_sample', 'lvye_pay_test'}
