# coding=utf-8
import os


class App:
    DEBUG = False
    TESTING = False


HOST_URL = 'http://pay.lvye.com'


class DataBase:
    HOST = os.environ['PAY_PUB_SITE_DATABASE_HOST']
    INSTANCE = 'lvye_pay'
    USERNAME = 'lvye_pay'
    PASSWORD = os.environ['PAY_PUB_SITE_DATABASE_PASSWORD']


class PayAPI:
    ROOT_URL = 'http://' + os.environ['PAY_API_SITE']


class Services:
    LEADER_SERVER = "http://leader.lvye.com"

