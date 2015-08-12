# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import os
from pytoolbox.conf.config import read_file


class App:
    TESTING = False
    DEBUG = False


class Host:
    API_GATEWAY = 'http://pay.lvye.com/api'

class DataBase:
    HOST = os.environ['PAY_API_SITE_DATABASE_HOST']
    INSTANCE = 'lvye_pay'
    USERNAME = 'lvye_pay'
    PASSWORD = os.environ['PAY_API_SITE_DATABASE_PASSWORD']


class Celery:
    HOST = os.environ['PAY_API_SITE_CELERY_HOST']
    PASSWORD = os.environ['PAY_API_SITE_CELERY_PASSWORD']


class LianLianPay:
    OID_PARTNER = '201507021000395502'

    class Sign:
        MD5_KEY = read_file('conf/keys/md5_key.txt')
        RSA_YT_PUB_KEY = read_file('conf/keys/yt_pub_key.txt')
        RSA_LVYE_PRI_KEY = read_file('conf/keys/lvye_pri_key.txt')
