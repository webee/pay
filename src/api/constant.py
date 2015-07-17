# coding=utf-8
from __future__ import unicode_literals


class SourceType(object):
    PAY = "PAY"
    WITHDRAW = "WITHDRAW"
    REFUND = "REFUND"
    PREPAID = "PREPAID"
    SETTLE = "SETTLE"
    TRANSFER = "转账"


class WithdrawResult(object):
    ## 提现冻结
    FROZEN = 'FROZEN'
    ## 提现成功
    SUCCESS = 'SUCCESS'
    ## 提现失败
    FAILED = 'FAILED'


class WithdrawStep(object):
    SECURED = "SECURED"
    EXPIRED = "EXPIRED"
    FROZEN = "FROZEN"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class response(object):
    TRUE_JUST_OK = {"ret": True}
    FALSE_REQUEST_FAILED = {"ret": False, "msg": "请求失败"}
    FALSE_BANKCARD_NOT_EXISTS = {"ret": False, "msg": "此银行卡不存在"}
    FALSE_AMOUNT_VALUE_ERROR = {"ret": False, "msg": "[amount]值错误"}
    FALSE_INSUFFICIENT_BALANCE = {"ret": False, "msg": "余额不足"}
    FALSE_ERROR_CREATING_ORDER = {"ret": False, "msg": "创建订单失败"}
