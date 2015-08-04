# coding=utf-8
import os

SECRET_KEY = os.environ.get('SECRET_KEY') or '.yek eyvl'
PROPAGATE_EXCEPTIONS = True
TESTING = False
DEBUG = True
LOGIN_DISABLED = False


class UserCenter:
    PASSPORT_LOGIN_URL = 'http://api.passport.lvye.com/oauth/toLogin/'
    AUTH_COOKIE = '4a7e7f902968e79c8b4e4975f316eb65'
    IS_PASSPORT_LOGIN_URL = 'http://api.passport.lvye.com/header/islogin.shtml'
    LOGIN_URL = 'http://account.lvye.cn/accounts/login/'


HOST_URL = 'http://pay.lvye.com'
