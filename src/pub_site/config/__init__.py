# coding=utf-8
import os

SECRET_KEY = os.environ.get('SECRET_KEY') or '.yek eyvl'
PROPAGATE_EXCEPTIONS = True
TESTING = True
DEBUG = True
IN_FILE = 'default'


class AccountCenter:
    CLIENT_ID = 123
    LOGIN_URL = "http://accounts.lvye.info/accounts/login/"
    VERIFY_URL = "http://accounts.lvye.info/accounts/verify/"
