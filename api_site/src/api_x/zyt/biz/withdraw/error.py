# coding=utf-8
from __future__ import unicode_literals


class WithdrawError(Exception):
    def __init__(self, msg):
        msg = msg.encode('utf-8') if isinstance(msg, unicode) else msg
        super(WithdrawError, self).__init__(msg)


class WithdrawFailedError(WithdrawError):
    def __init__(self, message=None):
        message = message or "apply for withdraw failed."
        super(WithdrawFailedError, self).__init__(message)
