# coding=utf-8


class App:
    TESTING = True


# ReverseProxy.HTTP_X_SCRIPT_NAME='/__'
HOST_URL = 'http://pay.lvye.com'


class Checkout:
    VALID_NETLOCS = ['pay.lvye.com']
    AES_KEY = "2HF5UKPIADDYBHDSKOVP9GMA80MU2IV2"
    PAYMENT_CHECKOUT_VALID_SECONDS = 1 * 60 * 60


class PayClientConfig:
    ROOT_URL = "http://pay.lvye.com/api/__"
    CHECKOUT_URL = 'http://pay.lvye.com/__/checkout/{sn}'
