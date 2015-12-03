# coding=utf-8
ROOT_URL = "http://dev_pay.lvye.com:5100"


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
        self.APP_NAME = name
        self.APPID = ""
        self.APP_SECRET = ""
        self.MCH_ID = ""
        self.API_KEY = ""
        self.CERT_PATH = ""
        self.CERT_KEY_PATH = ""

    @staticmethod
    def init_config(app_type, name, is_main=False):
        AppConfig.CONFIGS[name] = AppConfig(name, app_type, is_init=True)
        if is_main:
            AppConfig.CONFIGS['main'] = AppConfig.CONFIGS[name]

    def __repr__(self):
        return 'AppConfig<%s@%s>' % (self.APP_NAME, self.MCH_ID)


# init
WX_MAIN = 'ilvyewang'
AppConfig.init_config('public_account', 'ilvyewang', is_main=True)
AppConfig.init_config('app', 'lvye_skiing')

DEFAULT_ORDER_EXPIRATION_SECONDS = 7200  # 2 hours
UNIFIED_ORDER_URL = "https://api.mch.weixin.qq.com/pay/unifiedorder"
QUERY_ORDER_URL = "https://api.mch.weixin.qq.com/pay/orderquery"
REFUND_URL = "https://api.mch.weixin.qq.com/secapi/pay/refund"
QUERY_REFUND_URL = "https://api.mch.weixin.qq.com/pay/refundquery"
DOWNLOAD_BILL_URL = 'https://api.mch.weixin.qq.com/pay/downloadbill'

GET_CODE_URL = "https://open.weixin.qq.com/connect/oauth2/authorize?appid={appid}&redirect_uri=%s&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect"
GET_ACCESS_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token?appid={appid}&secret={secret}&code={code}&grant_type=authorization_code"


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
    SUCCESS = 'SUCCESS'  # 支付成功
    REFUND = 'REFUND'  # 转入退款
    NOTPAY = 'NOTPAY'  # 未支付
    CLOSED = 'CLOSED'  # 已关闭
    REVOKED = 'REVOKED'  # 已撤销
    USERPAYING = 'USERPAYING'  # 用户支付中
    PAYERROR = 'PAYERROR'  # 支付失败(其他原因，如银行返回失败)


class RefundStatus:
    SUCCESS = 'SUCCESS'  # 退款成功
    FAIL = 'FAIL'  # 退款失败
    PROCESSING = 'PROCESSING'  # 退款处理中
    NOTSURE = 'NOTSURE'  # 未确定，需要商户原退款单号重新发起
    CHANGE = 'CHANGE'  # 转入代发，退款到银行发现用户的卡作废或者冻结了，导致原路退款银行卡失败，资金回流到商户的现金帐号，需要商户人工干预，通过线下或者财付通转账的方式进行退款。


class BillType:
    ALL = 'ALL'  # 所有订单
    SUCCESS = 'SUCCESS'  # 成功支付的订单
    REFUND = 'REFUND'  # 退款订单
    REVOKED = 'REVOKED'  # 已撤销订单

