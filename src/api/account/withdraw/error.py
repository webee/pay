# coding=utf-8


if __name__ == '__main__':
    pass


class WithdrawError(Exception):
    def __init__(self, message=None):
        message = message or "withdraw error."
        super(WithdrawError, self).__init__(message)


class WithdrawRequestFailedError(WithdrawError):
    def __init__(self, withdraw_id, msg):
        message = "request withdraw failed: [{0}] [{1}].".format(withdraw_id, msg)
        super(WithdrawRequestFailedError, self).__init__(message)
        self.withdraw_id = withdraw_id
