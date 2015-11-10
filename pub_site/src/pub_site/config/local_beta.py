# coding=utf-8


class App:
    TESTING = True


class Checkout:
    ZYT_MAIN_PAGE = 'http://dev_pay.lvye.com:5102/main'
    VALID_NETLOCS = ['dev_pay.lvye.com:5102']


class PayClientConfig:
    ROOT_URL = "http://pay.lvye.com/api/__"
    CHECKOUT_URL = 'http://pay.lvye.com/__/checkout/{sn}'


HOST_URL = 'http://dev_pay.lvye.com:5102'
