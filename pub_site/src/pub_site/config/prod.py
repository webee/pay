# coding=utf-8
import os

class App:
    DEBUG = False
    TESTING = False

HOST_URL = 'http://pay.lvye.com'

class DataBase:
    HOST = os.environ['DATABASE_HOST']
    INSTANCE = 'lvye_pay'
    USERNAME = 'lvye_pay'
    PASSWORD = os.environ['DATABASE_PASSWORD']


class Services:
    LEADER_SERVER = "http://leader.lvye.com"

