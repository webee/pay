# coding=utf-8
from __future__ import unicode_literals


class source_type(object):
    PAY = "PAY"
    WITHDRAW = "WITHDRAW"
    REFUND = "REFUND"
    PREPAID = "PREPAID"
    SETTLE = "SETTLE"
    TRANSFER = "转账"


class event(object):
    STEP_SECURED = "SECURED"
    STEP_EXPIRED = "EXPIRED"
    STEP_FROZEN = "FROZEN"
    STEP_SUCCESS = "SUCCESS"
    STEP_FAILED = "FAILED"


class withdraw(object):
    # 提现订单结果
    ## 提现请求失败
    WITHDRAW_REQUEST_FAILED = 'REQUEST_FAILED'
    ## 提现冻结
    WITHDRAW_FROZEN = 'FROZEN'
    ## 提现成功
    WITHDRAW_SUCCESS = 'SUCCESS'
    ## 提现失败
    WITHDRAW_FAILED = 'FAILED'


class response(object):
    TRUE_JUST_OK = {"ret": True}
    FALSE_REQUEST_FAILED = {"ret": False, "msg": "请求失败"}
    FALSE_BANKCARD_NOT_EXISTS = {"ret": False, "msg": "此银行卡不存在"}
    FALSE_AMOUNT_VALUE_ERROR = {"ret": False, "msg": "[amount]值错误"}
    FALSE_INSUFFICIENT_BALANCE = {"ret": False, "msg": "余额不足"}
