# coding=utf-8
from pytoolbox.util import pmc_config

ROOT_URL = "http://pay.lvye.com/api"


class AppConfig:
    CONFIGS = {}

    def __init__(self, name='main', app_type=None, is_init=False):
        """
        :param app_type: is_init=True时不能为空
        :param name: is_init=True/False时不能为空
        :param is_init: 是否为初始化
        :return:
        """
        if not is_init:
            _config = AppConfig.CONFIGS[name]
            self.__dict__ = _config.__dict__
            return

        # init
        _main = pmc_config.load_yaml('conf/weixin/%s/%s/main.yaml' % (app_type, name))
        _pay_main = pmc_config.load_yaml('conf/weixin/%s/%s/pay/main.yaml' % (app_type, name))

        self.APP_NAME = name
        self.APPID = _main['AppID']
        self.APP_SECRET = _main['AppSecret']
        self.MCH_ID = _pay_main['MchID']
        self.API_KEY = pmc_config.read_string('conf/weixin/%s/%s/pay/api_key.txt' % (app_type, name))
        self.CERT_PATH = pmc_config.abstract_path('conf/weixin/%s/%s/pay/appclient_cert.pem' % (app_type, name))
        self.CERT_KEY_PATH = pmc_config.abstract_path('conf/weixin/%s/%s/pay/appclient_key.pem' % (app_type, name))

    @staticmethod
    def init_config(app_type, name, is_main=False):
        AppConfig.CONFIGS[name] = AppConfig(name, app_type, is_init=True)
        if is_main:
            AppConfig.CONFIGS['main'] = AppConfig.CONFIGS[name]


# init
WX_MAIN = 'ilvyewang'
AppConfig.init_config('public_account', 'ilvyewang', is_main=True)
AppConfig.init_config('app', 'lvye_skiing')


DEFAULT_ORDER_EXPIRATION_SECONDS = 604800  # 7 days
UNIFIED_ORDER_URL = "https://api.mch.weixin.qq.com/pay/unifiedorder"
QUERY_ORDER_URL = "https://api.mch.weixin.qq.com/pay/orderquery"
REFUND_URL = "https://api.mch.weixin.qq.com/secapi/pay/refund"
REFUND_QUERY_URL = "https://api.mch.weixin.qq.com/pay/refundquery"


class TradeType:
    # 统一下单接口
    JSAPI = 'JSAPI'  # 公众号支付
    NATIVE = 'NATIVE'  # 原生扫码支付
    APP = 'APP'  # app支付
    WAP = 'WAP'  # 手机浏览器H5支付

    # 刷卡支付接口
    MICROPAY = 'MICROPAY'  # 刷卡支付
