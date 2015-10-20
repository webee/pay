# coding=utf-8
from __future__ import unicode_literals


class DefaultUserDomain:
    SYSTEM_USER_DOMAIN_NAME = 'system'
    TEST_DOMAIN_NAME = 'testing'
    LVYE_CORP_DOMAIN_NAME = 'lvye_corp'
    LVYE_ACCOUNT_DOMAIN_NAME = 'lvye_account'

# 系统用户
SECURE_USER_NAME = 'secure'
# 绿野公司
LVYE_CORP_USER_NAME = 'lvye'


class VirtualAccountSystemType:
    ZYT = 'ZYT'
    TEST_PAY = 'TEST_PAY'
    LIANLIAN_PAY = 'LIANLIAN_PAY'
    WEIXIN_PAY = 'WEIXIN_PAY'
    ALI_PAY = 'ALI_PAY'


class TransactionType:
    PREPAID = 'PREPAID'
    PAYMENT = 'PAYMENT'
    TRANSFER = 'TRANSFER'
    REFUND = 'REFUND'
    WITHDRAW = 'WITHDRAW'


class PaymentTxState:
    CREATED = 'CREATED'
    # 已付钱，未收钱
    PAID_OUT = 'PAID_OUT'
    FAILED = 'FAILED'
    # 已付钱，已收钱
    SUCCESS = 'SUCCESS'
    SECURED = 'SECURED'
    REFUNDED = 'REFUNDED'
    REFUNDING = 'REFUNDING'


class PrepaidTxState:
    CREATED = 'CREATED'
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'


class RefundTxState:
    CREATED = 'CREATED'
    # payer已收到退款，payee未扣钱
    REFUNDED_IN = 'REFUNDED_IN'
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'


class WithdrawTxState:
    CREATED = 'CREATED'
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'
    FROZEN = 'FROZEN'
    PROCESSING = 'PROCESSING'


class TransactionState:
    CREATED = 'CREATED'
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'
    SECURED = 'SECURED'


class BankcardType:
    DEBIT = 'DEBIT'
    CREDIT = 'CREDIT'


class BankAccountType:
    PRIVATE = '0'
    CORPORATE = '1'


class RequestClientType:
    WEB = 'WEB'
    WAP = 'WAP'
    IOS = 'IOS'
    ANDROID = 'ANDROID'