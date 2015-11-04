# coding=utf-8
from pytoolbox.util.pmc_config import read_string


HOST_URL = "http://dev_pay.lvye.com:8089"


class App:
    import os

    SECRET_KEY = os.environ.get('SECRET_KEY') or '.yek eyvl'
    TESTING = False
    DEBUG = True

PAYEE = 'test001'


class PayClientConfig:
    MD5_KEY = read_string('conf/test/md5_key.txt')
    CHANNEL_PRI_KEY = read_string('conf/test/channel_pri_key.txt')

    # sample
    CHANNEL_NAME = 'zyt_sample'

    ROOT_URL = "http://dev_pay.lvye.com:5100"
    CHECKOUT_URL = 'http://pay.lvye.com/checkout/{sn}'
