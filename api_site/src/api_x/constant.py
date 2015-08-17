# coding=utf-8
from __future__ import unicode_literals

SYSTEM_USER_DOMAIN_NAME = '系统用户'
SECURE_USER_NAME = 'secure'


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


class TransactionState:
    CREATED = 'CREATED'
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'
    SECURED = 'SECURED'


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


class BankcardType:
    DEBIT = 'DEBIT'
    CREDIT = 'CREDIT'


class BankAccount:
    IS_PRIVATE_ACCOUNT = '0'
    IS_CORPORATE_ACCOUNT = '1'
