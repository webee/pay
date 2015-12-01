# coding=utf-8

ROOT_URL = "http://dev_pay.lvye.com:5100"


PID = ""
MD5_KEY = ""
ALI_PUB_KEY = ""
LVYE_PRI_KEY = ""


GATEWAY_URL = "https://mapi.alipay.com/gateway.do"
INPUT_CHARSET = 'utf-8'
PAYMENT_EXPIRE_TIME = '7d'


class Service:
    DIRECT_PAY_BY_USER = 'create_direct_pay_by_user'
    WAP_DIRECT_PAY_BY_USER = 'alipay.wap.create.direct.pay.by.user'
    MOBILE_SECURITYPAY_PAY = 'mobile.securitypay.pay'

    NOTIFY_VERIFY = 'notify_verify'


class PaymentType:
    WEB = 'WEB'
    WAP = 'WAP'
    APP = 'APP'


class PayMethod:
    DIRECT_PAY = 'directPay' # 余额支付
    CREDIT_PAY = 'creditPay' # 信用支付


class TradeStatus:
    WAIT_BUYER_PAY = 'WAIT_BUYER_PAY'
    TRADE_CLOSED = 'TRADE_CLOSED'
    TRADE_SUCCESS = 'TRADE_SUCCESS'
    TRADE_PENDING = 'TRADE_PENDING'
    TRADE_FINISHED = 'TRADE_FINISHED'


class RefundStatus:
    REFUND_SUCCESS = 'REFUND_SUCCESS'
    REFUND_CLOSED = 'REFUND_CLOSED'
