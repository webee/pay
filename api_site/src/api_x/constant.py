# coding=utf-8
from __future__ import unicode_literals


class DefaultUserDomain:
    SYSTEM_USER_DOMAIN_NAME = '系统用户'
    TEST_DOMAIN_NAME = '测试用户'
    LVYE_CORP_DOMAIN_NAME = '绿野公司用户'
    LVYE_ACCOUNT_DOMAIN_NAME = '绿野用户中心'

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


class PaymentTransactionState:
    CREATED = 'CREATED'
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'
    SECURED = 'SECURED'
    REFUNDED = 'REFUNDED'
    REFUNDING = 'REFUNDING'


class RefundTransactionState:
    CREATED = 'CREATED'
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'


class WithdrawTransactionState:
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
