# coding=utf-8
from __future__ import unicode_literals


class VASError(Exception):
    def __init__(self, message=None):
        message = message or "Virtual Account System error."
        super(VASError, self).__init__(message)


class InsufficientAvailableBalanceError(VASError):
    def __init__(self):
        message = "insufficient available balance error."
        super(InsufficientAvailableBalanceError, self).__init__(message)


class InsufficientFrozenBalanceError(VASError):
    def __init__(self):
        message = "insufficient frozen balance error."
        super(InsufficientFrozenBalanceError, self).__init__(message)


class AmountValueError(VASError):
    def __init__(self):
        message = "amount value error."
        super(AmountValueError, self).__init__(message)
