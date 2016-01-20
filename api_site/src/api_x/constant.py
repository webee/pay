# coding=utf-8
from __future__ import unicode_literals


class DefaultUserDomain:
    SYSTEM_USER_DOMAIN_NAME = 'system'
    TEST_DOMAIN_NAME = 'testing'
    LVYE_CORP_DOMAIN_NAME = 'lvye_corp'
    LVYE_ACCOUNT_DOMAIN_NAME = 'lvye_account'
    LVYE_CORP_MEMBER_DOMAIN_NAME = 'lvye_corp_member'

# 系统用户
SECURE_USER_NAME = 'secure'
# 绿野广告
LVYE_ADVERTISING_USER_NAME = 'lvye_advertising'
# 绿野提现手续费
LVYE_WITHDRAW_FEE_USER_NAME = 'lvye_withdraw_fee'
# 绿野滑雪
LVYE_SKIING_USER_NAME = 'lvye_skiing'


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
    # 支票
    CHEQUE = 'CHEQUE'


class PaymentChangeType:
    EXPIRED = 'EXPIRED'
    AMOUNT = 'AMOUNT'
    INFO = 'INFO'


class TxState:
    FINISHED = 'FINISHED'


class PaymentTxState:
    CREATED = 'CREATED'
    # 部分支付
    PARTIAL_PAID = 'PARTIAL_PAID'
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


class TransferTxState:
    CREATED = 'CREATED'
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'


class RefundTxState:
    CREATED = 'CREATED'
    PROCESSING = 'PROCESSING'
    # payer已收到退款，payee未扣钱
    REFUNDED_IN = 'REFUNDED_IN'
    FAILED = 'FAILED'
    BLOCK = 'BLOCK'
    SUCCESS = 'SUCCESS'


class WithdrawTxState:
    CREATED = 'CREATED'
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'
    FROZEN = 'FROZEN'
    PROCESSING = 'PROCESSING'


class ChequeTxState:
    CREATED = 'CREATED'
    # 冻结, 交结类支票的状态
    FROZEN = 'FROZEN'
    # 过期
    EXPIRED = 'EXPIRED'
    # 取消
    CANCELED = 'CANCELED'
    # 兑现
    CASHED = 'CASHED'


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


class PaymentOriginType:
    DUPLICATE = 'DUPLICATE'
    PART = 'PART'
