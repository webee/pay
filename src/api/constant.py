# coding=utf-8
from __future__ import unicode_literals


class BankcardType(object):
    DEBIT = 'DEBIT'
    CREDIT = 'CREDIT'


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
    TRANSFER = "TRANSFER"


class WithdrawState(object):
    FROZEN = 'FROZEN'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'


class WithdrawStep(object):
    FROZEN = "FROZEN"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class PaymentState(object):
    CREATED = 'CREATED'
    SECURED = 'SECURED'
    FAILED = 'FAILED'
    CONFIRMED = 'CONFIRMED'
    REFUNDING = 'REFUNDING'


class PayStep(object):
    SECURED = 'SECURED'
    CONFIRMED = 'CONFIRMED'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'


class RefundState(object):
    FROZEN = 'FROZEN'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'


class RefundStep(object):
    FROZEN = 'FROZEN'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'


class PrepaidStep(object):
    SUCCESS = "SUCCESS"
    FAILED = 'FAILED'


class TransferStep(object):
    FROZEN = "FROZEN"
    SUCCESS = "SUCCESS"
    FAILED = 'FAILED'
