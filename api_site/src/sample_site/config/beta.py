# coding=utf-8


class App:
    TESTING = True


HOST_URL = "http://dev_pay.lvye.com:8099"

PAYEE = '169658002'


class PayClientConfig:
    CHANNEL_NAME = 'lvye_pay_test'

    ROOT_URL = "http://pay.lvye.com/api/__"


CHECKOUT_URL = 'http://pay.lvye.com/__/checkout/{sn}'
