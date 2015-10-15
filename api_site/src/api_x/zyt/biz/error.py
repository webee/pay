# coding=utf-8
from __future__ import unicode_literals


class BizError(Exception):
    def __init__(self, message=None):
        message = message or 'biz error.'
        super(BizError, self).__init__(message)


class AmountError(BizError):
    def __init__(self, message):
        super(AmountError, self).__init__(message)


class AmountValueError(AmountError):
    def __init__(self, amount):
        message = "amount value error: [{0}]".format(amount)
        super(AmountValueError, self).__init__(message)


class NonPositiveAmountError(AmountError):
    def __init__(self, amount):
        message = "amount must be positive: [{0}]".format(amount)
        super(NonPositiveAmountError, self).__init__(message)


class NegativeAmountError(AmountError):
    def __init__(self, amount):
        message = "amount must not be negative: [{0}]".format(amount)
        super(NonPositiveAmountError, self).__init__(message)


class InsufficientAvailableBalanceError(BizError):
    def __init__(self):
        message = "insufficient available balance error."
        super(InsufficientAvailableBalanceError, self).__init__(message)


class RequestAPIError(BizError):
    def __init__(self, message=None):
        message = message or 'request api error.'
        super(RequestAPIError, self).__init__(message)


class TransactionNotFoundError(BizError):
    def __init__(self, message=None):
        message = message or 'transaction not found.'
        super(BizError, self).__init__(message)
