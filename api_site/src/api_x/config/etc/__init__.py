# coding=utf-8
from pytoolbox.util.pmc_config import read_string
from pytoolbox.util import public_key


class App:
    import os

    JSON_AS_ASCII = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or '.yek eyvl'
    TESTING = False
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql://lvye_pay:p@55word@127.0.0.1:3306/lvye_pay'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_SIZE = 30
    SQLALCHEMY_POOL_TIMEOUT = 60
    SQLALCHEMY_MAX_OVERFLOW = 60
    SQLALCHEMY_POOL_RECYCLE = 3600


HOST_URL = 'http://pay.lvye.com/api'
CHECKOUT_URL = 'http://pay.lvye.com/checkout/{sn}'


class Biz:
    # 是否全面开放
    IS_ALL_OPENED = False
    TX_SN_PREFIX = '__'
    IS_PROD = False

    PAYMENT_MAX_TRIAL_TIMES = 5
    PAYMENT_MAX_VALID_SECONDS = 6 * 24 * 60 * 60
    PAYMENT_CHECKOUT_VALID_SECONDS = 2 * 60 * 60
    ACTIVATED_EVAS = ['TEST_PAY', 'LIANLIAN_PAY', 'WEIXIN_PAY']
    VALID_NETLOCS = ['pay.lvye.com']

    class Channel:
        APP = "APP"
        WEB = "WEB"
        API = "API"
        WAP = "WAP"

KEY = read_string('conf/keys/key.txt')
LVYE_PRI_KEY = read_string('conf/keys/lvye_pri_key.txt')
LVYE_PUB_KEY = public_key.loads_b64encoded_key(LVYE_PRI_KEY).gen_public_key().b64encoded_binary_key_data()

TEST_MD5_KEY = read_string('conf/test/md5_key.txt')
TEST_CHANNEL_PUB_KEY = read_string('conf/test/channel_pub_key.txt')

TEST_CHANNELS = set()
