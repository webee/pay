# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.biz.error import BizError


class BadCashChequeTokenError(BizError):
    def __init__(self):
        message = 'bad cash cheque token error.'
        super(BadCashChequeTokenError, self).__init__(message)


class CashChequeError(BizError):
    def __init__(self, message):
        message = message or 'cash cheque error.'
        super(CashChequeError, self).__init__(message)
