# coding=utf-8
import os
from pytoolbox.util.pmc_config import read_string
from pytoolbox.util import public_key


class App:
    DEBUG = False
    TESTING = False

    # database
    SQLALCHEMY_DATABASE_URI = os.environ['PAY_API_SITE_DATABASE_URI']
    SQLALCHEMY_ECHO = False

HOST_URL = 'http://pay.lvye.com/api'
CHECKOUT_URL = 'http://pay.lvye.com/checkout/{sn}'


class Biz:
    TX_SN_PREFIX = ''
    IS_PROD = True

    ACTIVATED_EVAS = ['ZYT', 'LIANLIAN_PAY', 'WEIXIN_PAY', 'ALI_PAY']


KEY = read_string('conf/lvye/key.txt')
LVYE_PRI_KEY = read_string('conf/lvye/lvye_pri_key.txt')
LVYE_PUB_KEY = public_key.loads_b64encoded_key(LVYE_PRI_KEY).gen_public_key().b64encoded_binary_key_data()
