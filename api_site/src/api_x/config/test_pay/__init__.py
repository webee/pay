# coding=utf-8

MERCHANT_ID = '00001'
ROOT_URL = 'http://pay.lvye.com/api'


class Pay:
    URL = "http://dev_pay.lvye.com:8090/pay"

    class Channel:
        APP = "APP"
        WEB = "WEB"
        API = "API"
        WAP = "WAP"


class PaymentType:
    WEB = 'WEB'
    APP = 'APP'


class Refund:
    URL = "http://dev_pay.lvye.com:8090/refund"


class PayToBankcard:
    URL = "http://dev_pay.lvye.com:8090/pay_to_bankcard"
