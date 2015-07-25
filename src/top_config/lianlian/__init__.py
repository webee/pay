# coding=utf-8
from top_config.utils import read_string
PLATFORM = 'lvye.com'
OID_PARTNER = '201507021000395502'


class SignType:
    MD5 = 'MD5'
    RSA = 'RSA'


#MD5_KEY = 'x8LmLTRpmXtUcoRuLf7aUa50pwyl73j5kY/d4muoyfU='
MD5_KEY = read_string('conf/md5_key.txt')

# 银通公钥
YT_PUB_KEY = read_string('conf/yt_pub_key.txt')
# 商户私钥
LVYE_PRI_KEY = read_string('conf/lvye_pri_key.txt')


class Payment:
    class BusiPartner:
        VIRTUAL_GOODS = '101001'
        PHYSICAL_GOODS = '109001'

    DEFAULT_ORDER_EXPIRATION = '10080'

    VERSION = '1.0'
    URL = 'https://yintong.com.cn/payment/bankgateway.htm'
    REDIRECT_URL = '/pay/{uuid}'
    NOTIFY_URL = '/pay/{uuid}/notify'
    RETURN_URL = '/pay/{uuid}/result'


class Bankcard:
    BIN_QUERY_URL = 'https://yintong.com.cn/traderapi/bankcardquery.htm'


class PayToBankcard:
    VERSION = '1.2'
    URL = 'https://yintong.com.cn/traderapi/cardandpay.htm'
    NOTIFY_URL = '/withdraw/{uuid}/result'


class Order:
    URL = "https://yintong.com.cn/traderapi/orderquery.htm"


class Refund:
    URL = 'https://yintong.com.cn/traderapi/refund.htm'
    NOTIFY_URL = '/refund/{uuid}/notify'

    class Status:
        APPLY = '0'
        PROCESSING = '1'
        SUCCESS = '2'
        FAILED = '3'
