# coding=utf-8


class App:
    DEBUG = True


class PayClientConfig:
    CHANNEL_NAME = 'lvye_pay_test'

    CHECKOUT_URL = 'http://dev_pay.lvye.com:5102/checkout/{sn}'
