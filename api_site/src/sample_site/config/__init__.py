# coding=utf-8


HOST_URL = "http://localhost:8089"


class App:
    import os

    SECRET_KEY = os.environ.get('SECRET_KEY') or '.yek eyvl'
    TESTING = False
    DEBUG = True


class PayAPI:
    PREPAID_URL = 'http://pay.lvye.com/api/prepaid'
    PRE_PAY_URL = 'http://pay.lvye.com/api/pre_pay'
    CONFIRM_GUARANTEE_PAYMENT_URL = 'http://pay.lvye.com/api/pay/guarantee_payment/confirm'
    REFUND_URL = 'http://pay.lvye.com/api/refund'
