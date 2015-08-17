# coding=utf-8


class AmountError(Exception):
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