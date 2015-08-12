# -*- coding: utf-8 -*-


class App:
    PROPAGATE_EXCEPTIONS = True
    TESTING = False
    DEBUG = True


class Host:
    API_GATEWAY = 'http://127.0.0.1:5000'


class DataBase:
    HOST = ''
    PORT = 3306
    INSTANCE = 'lvye_pay'
    USERNAME = 'lvye_pay'
    PASSWORD = ''


class LianLianPay:
    OID_PARTNER = ''
    PLATFORM = 'lvye.com'

    class Sign:
        MD5_TYPE = 'MD5'
        RSA_TYPE = 'RSA'
        MD5_KEY = ''
        RSA_YT_PUB_KEY = ''
        RSA_LVYE_PRI_KEY = ''

    class Pay:
        URL = 'https://yintong.com.cn/payment/bankgateway.htm'
        VERSION = '1.0'
        BUSIPARTNER_VIRTUAL_GOODS = '101001'
        BUSIPARTNER_PHYSICAL_GOODS = '109001'
        DEFAULT_ORDER_EXPIRATION = 10080

    class PayToBankcard:
        URL = 'https://yintong.com.cn/traderapi/cardandpay.htm'
        VERSION = '1.2'

        class Result:
            SUCCESS = 'SUCCESS'
            WAITING = 'WAITING'
            FAILURE = 'FAILURE'
            CANCEL = 'CANCEL'
            PROCESSING = 'PROCESSING'

    class OrderQuery:
        URL = 'https://yintong.com.cn/traderapi/orderquery.htm'
        VERSION = '1.1'
        PAY_TYPEDC = 0
        WITHDRAW_TYPEDC = 0

    class Refund:
        URL = 'https://yintong.com.cn/traderapi/refund.htm'

        class Status:
            APPLIED = 0
            PROCESSING = 1
            SUCCESS = 2
            FAILED = 3

    class BankcardBinQuery:
        URL = 'https://yintong.com.cn/traderapi/bankcardquery.htm'


class ZiYouTong:
    VALIDATE_SIGNATURE = True

    class CallbackInterface:
        PAY_URL = '/pay/{uuid}'
        PAY_RETURN_URL = '/callback/pay/{uuid}/result'
        PAY_NOTIFY_URL = '/callback/pay/{uuid}/notify'
        PAY_TO_BANKCARD_NOTIFY_URL = '/callback/withdraw/{uuid}/notify'
        REFUND_NOTIFY_URL = '/callback/refund/{uuid}/notify'


class Celery:
    HOST = ''
    USERNAME = 'lvye_pay'
    PASSWORD = ''
    INSTANCE = 'lvye_pay_api'
