# -*- coding: utf-8 -*-


class App:
    TESTING = False


class Host:
    API_GATEWAY = 'http://pay.lvye.com'


class DataBase:
    HOST = 'localhost'
    PASSWORD = 'p@55word'


class LianLianPay:
    OID_PARTNER = '201507021000395502'

    class Sign:
        MD5_KEY = ''
        RSA_YT_PUB_KEY = ''
        RSA_LVYE_PRI_KEY = ''


class ZiYouTong:
    VALIDATE_SIGNATURE = True