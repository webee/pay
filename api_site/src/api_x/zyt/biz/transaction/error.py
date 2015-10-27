# coding=utf-8
from __future__ import unicode_literals


class TransactionError(Exception):
    def __init__(self, msg):
        msg = msg.encode('utf-8') if isinstance(msg, unicode) else msg
        super(TransactionError, self).__init__(msg)


class TransactionNotFoundError(TransactionError):
    def __init__(self, tx_id):
        msg = "transaction: [id: {0}] state error.".format(tx_id)
        super(TransactionNotFoundError, self).__init__(msg)


class TransactionStateError(TransactionError):
    def __init__(self, msg=None):
        msg = msg or "tx state error."
        super(TransactionStateError, self).__init__(msg)