# coding=utf-8
import os
from pytoolbox.util.pmc_config import read_string


class App:
    DEBUG = False
    TESTING = False

    # database
    SQLALCHEMY_DATABASE_URI = os.environ['PAY_PUB_SITE_DATABASE_URI']
    SQLALCHEMY_ECHO = False


HOST_URL = 'http://pay.lvye.com'


class PayClientConfig:
    MD5_KEY = read_string('conf/keys/md5_key.txt')
    CHANNEL_PRI_KEY = read_string('conf/keys/channel_pri_key.txt')

    ROOT_URL = os.environ['PAY_API_SITE'] or 'http://pay.lvye.com/api'

