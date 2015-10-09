# coding=utf-8
from __future__ import unicode_literals

from ..error import BizError


class PaymentError(BizError):
    def __init__(self, message):
        super(PaymentError, self).__init__(message)


class AlreadyPaidError(PaymentError):
    def __init__(self, order_id):
        message = "order [{0}] already paid.".format(order_id)
        super(AlreadyPaidError, self).__init__(message)

