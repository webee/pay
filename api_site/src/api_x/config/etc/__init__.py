# coding=utf-8
from pytoolbox.util.pmc_config import read_string


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

    ENTRY_PREFIX = '/__'


HOST_URL = 'http://pay.lvye.com/api'


class Biz:
    # 是否全面开放
    IS_ALL_OPENED = False
    TX_SN_PREFIX = '__'

    ACTIVATED_EVAS = ['TEST_PAY', 'LIANLIAN_PAY']


LVYE_PRI_KEY = read_string('conf/keys/lvye_pri_key.txt')
TEST_MD5_KEY = read_string('conf/test/md5_key.txt')
TEST_CHANNEL_PUB_KEY = read_string('conf/test/channel_pub_key.txt')
