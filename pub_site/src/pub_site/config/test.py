# coding=utf-8


class App:
    DEBUG = True


class Checkout:
    VALID_NETLOCS = ['dev_pay.lvye.com:5102']


class PayClientConfig:
    ZYT_MAIN_PAGE = 'http://dev_pay.lvye.com:5102/main'
    ROOT_URL = "http://dev_pay.lvye.com:5000"
    CHECKOUT_URL = 'http://dev_pay.lvye.com:5102/checkout/{sn}'


HOST_URL = 'http://dev_pay.lvye.com:5102'
