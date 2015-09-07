# coding=utf-8
import os
from pytoolbox.util import pmc_config
from pytoolbox.util.pmc_config import read_string


class App:
    ADMINS = ['liufan@lvye.com', 'yiwang@lvye.com', 'mengyu@lvye.com', 'zhoushiwei@lvye.com']
    JSON_AS_ASCII = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or '.yek eyvl'
    TESTING = False
    DEBUG = True
    LOGIN_DISABLED = False
    WTF_CSRF_SECRET_KEY = 'a random string'

    SQLALCHEMY_DATABASE_URI = 'mysql://lvye_pay:p@55word@127.0.0.1:3306/lvye_pay_pub'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_SIZE = 30
    SQLALCHEMY_POOL_TIMEOUT = 60
    SQLALCHEMY_MAX_OVERFLOW = 60
    SQLALCHEMY_POOL_RECYCLE = 3600


class UserCenter:
    PASSPORT_LOGIN_URL = 'http://api.passport.lvye.com/oauth/toLogin/'
    AUTH_COOKIE = '4a7e7f902968e79c8b4e4975f316eb65'
    IS_PASSPORT_LOGIN_URL = 'http://api.passport.lvye.com/header/islogin.shtml'
    LOGIN_URL = 'http://account.lvye.cn/accounts/login/'
    LOGOUT_URL = 'http://account.lvye.cn/accounts/logout/'

IS_PROD = False
HOST_URL = 'http://pay.lvye.com'

# 绿野公司域和用户
LVYE_CORP_DOMAIN_NAME = 'lvye_corp'
LVYE_USER_NAME = 'lvye'

# TODO: 同步该配置
IS_ALL_OPENED = False


# # pay api
class PayClientConfig:
    MD5_KEY = read_string('conf/test/md5_key.txt')
    CHANNEL_PRI_KEY = read_string('conf/test/channel_pri_key.txt')

    CHANNEL_NAME = 'lvye_pay_site'

    ROOT_URL = "http://pay.lvye.com/api"


# #### data #######
def load_provinces_and_cities(file_path):
    from os import path
    from collections import OrderedDict
    import codecs

    utf8reader = codecs.getreader('utf-8')

    with utf8reader(open(path.join(pmc_config.get_project_root(), file_path))) as fin:
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


class SMSConfig:
    URL = 'http://sdk999ws.eucp.b2m.cn:8080/sdkproxy/sendsms.action'
    CD_KEY = '9SDK-EMY-0999-JBQOO'
    PASSWORD = '506260'


class PaymentType:
    DIRECT = 'DIRECT'
    GUARANTEE = 'GUARANTEE'
