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
        self.CERT_PATH = pmc_config.abstract_path('conf/weixin/%s/%s/pay/apiclient_cert.pem' % (app_type, name))
        self.CERT_KEY_PATH = pmc_config.abstract_path('conf/weixin/%s/%s/pay/apiclient_key.pem' % (app_type, name))

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
QUERY_REFUND_URL = "https://api.mch.weixin.qq.com/pay/refundquery"


class TradeType:
    # 统一下单接口
    JSAPI = 'JSAPI'  # 公众号支付
    NATIVE = 'NATIVE'  # 原生扫码支付
    APP = 'APP'  # app支付
    WAP = 'WAP'  # 手机浏览器H5支付

    # 刷卡支付接口
    MICROPAY = 'MICROPAY'  # 刷卡支付


class PaymentType:
    JSAPI = 'JSAPI'
    NATIVE = 'NATIVE'
    APP = 'APP'

    MICROPAY = 'MICROPAY'


class TradeState:
    SUCCESS = 'SUCCESS' #支付成功
    REFUND = 'REFUND' #转入退款
    NOTPAY = 'NOTPAY' #未支付
    CLOSED = 'CLOSED' #已关闭
    REVOKED = 'REVOKED' #已撤销
    USERPAYING = 'USERPAYING' #用户支付中
    PAYERROR = 'PAYERROR' #支付失败(其他原因，如银行返回失败)


class RefundStatus:
    SUCCESS = 'SUCCESS' #退款成功
    FAIL = 'FAIL' #退款失败
    PROCESSING = 'PROCESSING' #退款处理中
    NOTSURE = 'NOTSURE' #未确定，需要商户原退款单号重新发起
    CHANGE = 'CHANGE' #转入代发，退款到银行发现用户的卡作废或者冻结了，导致原路退款银行卡失败，资金回流到商户的现金帐号，需要商户人工干预，通过线下或者财付通转账的方式进行退款。
