# coding=utf-8
from __future__ import unicode_literals


class WithdrawError(Exception):
    def __init__(self, message):
        super(WithdrawError, self).__init__(message)


class WithdrawFailedError(WithdrawError):
    def __init__(self, message=None):
        message = message or "apply for withdraw failed."
        super(WithdrawFailedError, self).__init__(message)
