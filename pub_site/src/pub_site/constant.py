# coding=utf-8
from __future__ import unicode_literals


SOURCE_MESSAGES = {
    'WITHDRAW:FROZEN': '提现',
    'WITHDRAW:FAILED': '提现失败',
    'PREPAID': '充值',
    'PAY': '支付',
    'REFUND': '退款',
    'TRANSFER': '转账',
}


class PayType:
    def __init__(self):
        pass

    BY_BALANCE = 0
    BY_BANKCARD = 1


class TradeType:
    def __init__(self):
        pass

    WITHDRAW = 0
    PAY_TO_LVYE = 1
