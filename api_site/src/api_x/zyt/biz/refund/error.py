# coding=utf-8
from __future__ import unicode_literals


class RefundError(Exception):
    def __init__(self, message):
        message = message.encode('utf-8') if isinstance(message, unicode) else message
        super(RefundError, self).__init__(message)


class NoPaymentFoundError(RefundError):
    def __init__(self, channel_id, order_id):
        message = "Cannot find any valid payment record with [channel_id={0}, order_id={1}]." \
            .format(channel_id, order_id)
        super(NoPaymentFoundError, self).__init__(message)


class NoRefundFoundError(RefundError):
    def __init__(self, client_id, refund_id):
        message = "refund not found: [client_id={0}, refund_id: {1}].".format(client_id, refund_id)
        super(NoRefundFoundError, self).__init__(message)


class RefundFailedError(RefundError):
    def __init__(self, message=None):
        message = message or "apply for refund failed."
        super(RefundFailedError, self).__init__(message)


class PaymentNotPaidError(RefundError):
    def __init__(self, message=None):
        message = message or "payment has not paid."
        super(PaymentNotPaidError, self).__init__(message)


class PaymentNotRefundableError(RefundError):
    def __init__(self, message=None):
        message = message or "payment not refundable."
        super(PaymentNotRefundableError, self).__init__(message)


class PaymentIsRefundingError(RefundError):
    def __init__(self, message=None):
        message = message or "payment is refunding."
        super(PaymentIsRefundingError, self).__init__(message)


class PaymentRefundedError(RefundError):
    def __init__(self, message=None):
        message = message or "payment has refunded."
        super(PaymentRefundedError, self).__init__(message)


class RefundStateMissMatchError(RefundError):
    def __init__(self, message=None):
        message = message or "refund state miss match."
        super(RefundStateMissMatchError, self).__init__(message)


class RefundAmountError(RefundError):
    def __init__(self, paid_amount, refunded_amount, refund_amount):
        message = "refund amount error: [paid_amount: {0}, refunded_amount: {1}, refund_amount: {2}]."\
            .format(paid_amount, refunded_amount, refund_amount)
        super(RefundAmountError, self).__init__(message)


class RefundBalanceError(RefundError):
    def __init__(self, amount, balance):
        message = "refund balance error: [amount: {0}, balance: {1}.".format(amount, balance)
        super(RefundBalanceError, self).__init__(message)
