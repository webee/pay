# coding=utf-8


class InsufficientAvailableBalanceError(Exception):
    def __init__(self):
        message = "insufficient available balance error."
        super(InsufficientAvailableBalanceError, self).__init__(message)


class InsufficientFrozenBalanceError(Exception):
    def __init__(self):
        message = "insufficient frozen balance error."
        super(InsufficientFrozenBalanceError, self).__init__(message)
