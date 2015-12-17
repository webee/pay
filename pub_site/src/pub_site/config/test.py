# coding=utf-8


class App:
    DEBUG = True


class Checkout:
    ZYT_MAIN_PAGE = 'http://dev_pay.lvye.com:5102/main'
    VALID_NETLOCS = ['dev_pay.lvye.com:5102']


class LvyePaySiteClientConfig:
    ROOT_URL = "http://dev_pay.lvye.com:5000"
    CHECKOUT_URL = 'http://dev_pay.lvye.com:5102/checkout/{sn}'


class LvyeCorpPaySiteClientConfig:
    ROOT_URL = "http://dev_pay.lvye.com:5000"
    CHECKOUT_URL = 'http://dev_pay.lvye.com:5102/checkout/{sn}'


HOST_URL = 'http://dev_pay.lvye.com:5102'
