# coding=utf-8


class NoBankcardFoundError(Exception):
    def __init__(self, account_id, bankcard_id):
        message = "Cannot find bankcard with [account_id={0}, bankcard_id={1}].".format(account_id, bankcard_id)
        super(NoBankcardFoundError, self).__init__(message)


class InsufficientBalanceError(Exception):
    def __init__(self):
        message = "insufficient balance error."
        super(InsufficientBalanceError, self).__init__(message)


class WithdrawError(Exception):
    def __init__(self, message=None):
        message = message or "withdraw error."
        super(WithdrawError, self).__init__(message)


class WithdrawRequestFailedError(WithdrawError):
    def __init__(self, withdraw_id):
        message = "request withdraw failed: [{0}].".format(withdraw_id)
        super(WithdrawRequestFailedError, self).__init__(message)
        self.withdraw_id = withdraw_id
