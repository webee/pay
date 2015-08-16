# coding=utf-8


HOST_URL = "http://dev_pay.lvye.com:8089"


class App:
    import os

    SECRET_KEY = os.environ.get('SECRET_KEY') or '.yek eyvl'
    TESTING = False
    DEBUG = True


class PayAPI:
    PREPAID_URL = 'http://dev_pay.lvye.com:8088/prepaid'
    PRE_PAY_URL = 'http://dev_pay.lvye.com:8088/pre_pay'
    CONFIRM_GUARANTEE_PAYMENT_URL = 'http://dev_pay.lvye.com:8088/pay/guarantee_payment/confirm'
