# coding=utf-8

ROOT_URL = "http://dev_pay.lvye.com:5100"

OID_PARTNER = '201408071000001546'
PLATFORM = OID_PARTNER

MD5_KEY = '201408071000001546_test_20140815'
YT_PUB_KEY = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCSS/DiwdCf/aZsxxcacDnooGph3d2JOj5GXWi+q3gznZauZjkNP8SKl3J2liP0O6rU/Y/29+IUe+GTMhMOFJuZm1htAtKiu5ekW0GlBMWxf4FPkYlQkPE0FtaoMP3gYfh+OwI+fIRrpW3ySn3mScnc6Z700nU/VYrRkfcSCbSnRwIDAQAB"
LVYE_PRI_KEY = "MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBAOilN4tR7HpNYvSBra/DzebemoAiGtGeaxa+qebx/O2YAdUFPI+xTKTX2ETyqSzGfbxXpmSax7tXOdoa3uyaFnhKRGRvLdq1kTSTu7q5s6gTryxVH2m62Py8Pw0sKcuuV0CxtxkrxUzGQN+QSxf+TyNAv5rYi/ayvsDgWdB3cRqbAgMBAAECgYEAj02d/jqTcO6UQspSY484GLsL7luTq4Vqr5L4cyKiSvQ0RLQ6DsUG0g+Gz0muPb9ymf5fp17UIyjioN+ma5WquncHGm6ElIuRv2jYbGOnl9q2cMyNsAZCiSWfR++op+6UZbzpoNDiYzeKbNUz6L1fJjzCt52w/RbkDncJd2mVDRkCQQD/Uz3QnrWfCeWmBbsAZVoM57n01k7hyLWmDMYoKh8vnzKjrWScDkaQ6qGTbPVL3x0EBoxgb/smnT6/A5XyB9bvAkEA6UKhP1KLi/ImaLFUgLvEvmbUrpzY2I1+jgdsoj9Bm4a8K+KROsnNAIvRsKNgJPWd64uuQntUFPKkcyfBV1MXFQJBAJGs3Mf6xYVIEE75VgiTyx0x2VdoLvmDmqBzCVxBLCnvmuToOU8QlhJ4zFdhA1OWqOdzFQSw34rYjMRPN24wKuECQEqpYhVzpWkA9BxUjli6QUo0feT6HUqLV7O8WqBAIQ7X/IkLdzLa/vwqxM6GLLMHzylixz9OXGZsGAkn83GxDdUCQA9+pQOitY0WranUHeZFKWAHZszSjtbe6wDAdiKdXCfig0/rOdxAODCbQrQs7PYy1ed8DuVQlHPwRGtokVGHATU="


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

    class Channel:
        APP = "10"
        WEB = "13"
        API = "15"
        WAP = "16"


class PaymentType:
    WEB = 'WEB'
    WAP = 'WAP'
    APP = 'APP'


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
    USER_BANKCARD_URL = 'https://yintong.com.cn/traderapi/userbankcard.htm'
    UNBIND_USER_BANKCARD_URL = 'https://yintong.com.cn/traderapi/bankcardunbind.htm'
    BIN_QUERY_URL = 'https://yintong.com.cn/traderapi/bankcardquery.htm'


class OrderQuery:
    VERSION = "1.1"
    URL = "https://yintong.com.cn/traderapi/orderquery.htm"

    class TypeDC:
        PAY = "0"
        WITHDRAW = "1"


class Ftp:
    # beta, prod only.
    HOSTNAME = ""
    PORT = 0
    USERNAME = ""
    PASSWORD = ""

    JYMX_PATH = "bjlysy/{oid_partner}/JYMX_{oid_partner}_{date}.csv"
