# coding=utf-8
import os
from pytoolbox.util.pmc_config import read_string


class App:
    DEBUG = False
    TESTING = False

    # database
    SQLALCHEMY_DATABASE_URI = os.environ['PAY_PUB_SITE_DATABASE_URI']
    SQLALCHEMY_ECHO = False


class Checkout:
    VALID_NETLOCS = ['pay.lvye.com']
    AES_KEY = read_string('conf/checkout/aes_key.txt')
    PAYMENT_CHECKOUT_VALID_SECONDS = 2 * 60 * 60


IS_PROD = True
HOST_URL = 'http://pay.lvye.com'


class LvyePaySitePayClientConfig:
    MD5_KEY = read_string('conf/lvye_pay_site/md5_key.txt')
    CHANNEL_PRI_KEY = read_string('conf/lvye_pay_site/channel_pri_key.txt')

    ROOT_URL = os.environ['PAY_API_SITE'] or 'http://pay.lvye.com/api'


class LvyeCorpPaySitePayClientConfig:
    MD5_KEY = read_string('conf/lvye_corp_pay_site/md5_key.txt')
    CHANNEL_PRI_KEY = read_string('conf/lvye_corp_pay_site/channel_pri_key.txt')

    ROOT_URL = os.environ['PAY_API_SITE'] or 'http://pay.lvye.com/api'
