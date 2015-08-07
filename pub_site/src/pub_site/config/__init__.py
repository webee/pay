# coding=utf-8
import os
from pytoolbox import conf


class App:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '.yek eyvl'
    PROPAGATE_EXCEPTIONS = True
    TESTING = False
    DEBUG = True
    LOGIN_DISABLED = False
    WTF_CSRF_SECRET_KEY = 'a random string'


class UserCenter:
    PASSPORT_LOGIN_URL = 'http://api.passport.lvye.com/oauth/toLogin/'
    AUTH_COOKIE = '4a7e7f902968e79c8b4e4975f316eb65'
    IS_PASSPORT_LOGIN_URL = 'http://api.passport.lvye.com/header/islogin.shtml'
    LOGIN_URL = 'http://account.lvye.cn/accounts/login/'
    LOGOUT_URL = 'http://account.lvye.cn/accounts/logout/'


HOST_URL = 'http://pay.lvye.com'

# 绿野用户中心
USER_DOMAIN_ID = 1


# # pay api
class PayAPI:
    ROOT_URL = "http://pay.lvye.com/"
    GET_ACCOUNT_INFO_URL = "user_domains/{user_domain_id}/users/{uid}/account"
    GET_USER_BALANCE_URL = "accounts/{account_id}/balance"
    GET_USER_CASH_RECORDS_URL = "accounts/{account_id}/cash_records"


# #### data #######
def load_provinces_and_cities(filepath):
    from os import path
    from collections import OrderedDict
    import codecs

    UTF8Reader = codecs.getreader('utf-8')

    with UTF8Reader(open(path.join(conf.project_root(), filepath))) as fin:
        provinces = OrderedDict()
        cities = OrderedDict()
        for line in fin:
            province, province_code, city, city_code = line.strip().split('\t')
            provinces.setdefault(province_code, province)
            cities_in_current_province = cities.setdefault(province_code, OrderedDict())
            cities_in_current_province.setdefault(city_code, city)
    return provinces, cities


class Data:
    PROVINCES, CITIES = load_provinces_and_cities('conf/province_and_city_code.txt')


class Services:
    LEADER_SERVER = "http://tleader.lvye.com"


class SMS:
    URL = 'http://sdk999ws.eucp.b2m.cn:8080/sdkproxy/sendsms.action'
    CD_KEY = '9SDK-EMY-0999-JBQOO'
    PASSWORD = '506260'
