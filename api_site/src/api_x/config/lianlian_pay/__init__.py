# coding=utf-8
from pytoolbox.util.pmc_config import read_string
PLATFORM = 'lvye.com'
OID_PARTNER = '201507021000395502'

ROOT_URL = "http://pay.lvye.com/api"


MD5_KEY = read_string('conf/keys/md5_key.txt')
YT_PUB_KEY = read_string('conf/keys/yt_pub_key.txt')
LVYE_PRI_KEY = read_string('conf/keys/lvye_pri_key.txt')


class AppRequest:
    ANDROID = '1'
    IOS = '2'
    WAP = '3'


class Payment:
    VERSION = '1.0'
    URL = 'https://yintong.com.cn/payment/bankgateway.htm'

    class BusiPartner:
        VIRTUAL_GOODS = '101001'
        PHYSICAL_GOODS = '109001'

    DEFAULT_ORDER_EXPIRATION = '10080'

    class Wap:
        VERSION = '1.1'
        URL = 'https://yintong.com.cn/llpayh5/payment.htm'


class Refund:
    URL = 'https://yintong.com.cn/traderapi/refund.htm'
    QUERY_URL = 'https://yintong.com.cn/traderapi/refundquery.htm'

    class Status:
        APPLY = '0'
        PROCESSING = '1'
        SUCCESS = '2'
        FAILED = '3'


class PayToBankcard:
    VERSION = '1.2'
    URL = 'https://yintong.com.cn/traderapi/cardandpay.htm'

    class Result:
        SUCCESS = 'SUCCESS'
        WAITING = 'WAITING'
        FAILURE = 'FAILURE'
        CANCEL = 'CANCEL'
        PROCESSING = 'PROCESSING'


class Bankcard:
    BIN_QUERY_URL = 'https://yintong.com.cn/traderapi/bankcardquery.htm'


class OrderQuery:
    VERSION = "1.1"
    URL = "https://yintong.com.cn/traderapi/orderquery.htm"

    class TypeDC:
        PAY = "0"
        WITHDRAW = "1"
