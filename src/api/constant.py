# coding=utf-8
from __future__ import unicode_literals


class BookkeepingSide(object):
    DEBIT = 'DEBIT'
    CREDIT = 'CREDIT'
    BOTH = 'BOTH'


class SourceType(object):
    PAY = "PAY"
    WITHDRAW = "WITHDRAW"
    REFUND = "REFUND"
    PREPAID = "PREPAID"
    SETTLE = "SETTLE"
    TRANSFER = "转账"


class WithdrawResult(object):
    FROZEN = 'FROZEN'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'


class PayStep(object):
    SECURED = 'SECURED'
    CONFIRMED = 'CONFIRMED'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'


class WithdrawStep(object):
    SECURED = "SECURED"
    EXPIRED = "EXPIRED"
    FROZEN = "FROZEN"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class RefundStep(object):
    FROZEN = "FROZEN"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
