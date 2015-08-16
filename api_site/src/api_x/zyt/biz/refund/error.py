# coding=utf-8
from __future__ import unicode_literals


class NoPaymentFoundError(Exception):
    def __init__(self, channel_id, order_id):
        message = "Cannot find any valid payment record with [channel_id={0}, order_id={1}]." \
            .format(channel_id, order_id)
        super(NoPaymentFoundError, self).__init__(message)


class NoRefundFoundError(Exception):
    def __init__(self, client_id, refund_id):
        message = "refund not found: [client_id={0}, refund_id: {1}].".format(client_id, refund_id)
        super(NoRefundFoundError, self).__init__(message)


class RefundError(Exception):
    def __init__(self, message):
        super(RefundError, self).__init__(message)


class RefundFailedError(RefundError):
    def __init__(self, message=None):
        message = message or "apply for refund failed."
        super(RefundFailedError, self).__init__(message)


class PaymentNotRefundableError(RefundError):
    def __init__(self, message=None):
        message = message or "payment not refundable."
        super(PaymentNotRefundableError, self).__init__(message)


class RefundStateMissMatchError(RefundError):
    def __init__(self, message=None):
        message = message or "refund state miss match."
        super(RefundStateMissMatchError, self).__init__(message)


class RefundAmountError(RefundError):
    def __init__(self, amount):
        message = "refund amount error: [{0}].".format(amount)
        super(RefundAmountError, self).__init__(message)
