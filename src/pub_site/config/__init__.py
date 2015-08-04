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
    LOGOUT_URL = 'http://account.lvye.cn/accounts/logout/'


HOST_URL = 'http://pay.lvye.com'


##### data #######

def load_provinces_and_cities(filepath):
    from tools import pmc_config
    from os import path
    from collections import OrderedDict
    import codecs
    UTF8Reader = codecs.getreader('utf-8')

    with UTF8Reader(open(path.join(pmc_config.get_project_root(), filepath))) as fin:
        data = OrderedDict()
        for line in fin:
            p, pc, c, cc = line.strip().split('\t')
            pd = data.setdefault(p, {'c': pc, 'cities': OrderedDict()})
            pd['cities'][c] = {'c': cc}
    return data


class Data:
    PROVINCES_AND_CITIES = load_provinces_and_cities('conf/province_and_city_code.txt')

class Services:
    LEADER_SERVER = "http://tleader.lvye.com"
