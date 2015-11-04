# coding=utf-8


class App:
    TESTING = True


# ReverseProxy.HTTP_X_SCRIPT_NAME='/__'
HOST_URL = 'http://pay.lvye.com'


class PayClientConfig:
    ROOT_URL = "http://pay.lvye.com/api/__"
    CHECKOUT_URL = 'http://pay.lvye.com/__/checkout/{sn}'
