# coding=utf-8
import os


class App:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '.yek eyvl'
    PROPAGATE_EXCEPTIONS = True
    TESTING = False
    DEBUG = True
    LOGIN_DISABLED = False
    WTF_CSRF_SECRET_KEY = 'a random string'


class DataBase:
    HOST = 'localhost'
    PORT = 3306
    INSTANCE = 'lvye_pay'
    USERNAME = 'lvye_pay'
    PASSWORD = 'p@55word'

class Host:
    API_SITE = ''
