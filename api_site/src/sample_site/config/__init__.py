# coding=utf-8
from pytoolbox.util.pmc_config import read_string


HOST_URL = "http://localhost:8089"


class App:
    import os

    SECRET_KEY = os.environ.get('SECRET_KEY') or '.yek eyvl'
    TESTING = False
    DEBUG = True

PAYEE = 'test001'


class PayClientConfig:
    MD5_KEY = read_string('conf/test/md5_key.txt')
    LVYE_PUB_KEY = read_string('conf/test/lvye_pub_key.txt')
    CHANNEL_PRI_KEY = read_string('conf/test/channel_pri_key.txt')

    # 测试用户
    USER_DOMAIN_NAME = 'testing'
    # sample
    CHANNEL_NAME = 'zyt_sample'

    ROOT_URL = "http://pay.lvye.com/api"
