# -*- coding: utf-8 -*-


class App:
    TESTING = False


class Host:
    API_GATEWAY = 'http://pay.lvye.com'


class LianLianPay:
    OID_PARTNER = '201507021000395502'

    class Sign:
        MD5_KEY = ''
        RSA_YT_PUB_KEY = ''
        RSA_LVYE_PRI_KEY = ''


class ZiYouTong:
    VALIDATE_SIGNATURE = True


class Celery:
    HOST = '127.0.0.1:5672'
    PASSWORD = 'p@55word'