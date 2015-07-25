# coding=utf-8


class NoPaymentFoundError(Exception):
    def __init__(self, client_id, order_id):
        message = "Cannot find any valid pay transaction with [client_id={0}, order_id={1}]." \
            .format(client_id, order_id)
        super(NoPaymentFoundError, self).__init__(message)


class NoRefundFoundError(Exception):
    def __init__(self, client_id, refund_id):
        message = "refund not found: [client_id={0}, refund_id: {1}].".format(client_id, refund_id)
        super(NoRefundFoundError, self).__init__(message)


class RefundError(Exception):
    def __init__(self, message):
        super(RefundError, self).__init__(message)


class RefundFailedError(RefundError):
    def __init__(self, refund_id):
        message = "apply for refund failed."
        super(RefundFailedError, self).__init__(message)
        self.refund_id = refund_id


class PaymentStateMissMatchError(RefundError):
    def __init__(self):
        message = "payment state miss match."
        super(PaymentStateMissMatchError, self).__init__(message)


class RefundStateMissMatchError(RefundError):
    def __init__(self):
        message = "refund state miss match."
        super(RefundStateMissMatchError, self).__init__(message)


class RefundAmountError(RefundError):
    def __init__(self, amount):
        message = "refund amount error: [{0}].".format(amount)
        super(RefundStateMissMatchError, self).__init__(message)
