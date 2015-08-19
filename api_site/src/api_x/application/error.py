# coding=utf-8
from __future__ import unicode_literals


class BankcardError(Exception):
    def __init__(self, message):
        super(BankcardError, self).__init__(message)


class InvalidCardNoError(BankcardError):
    def __init__(self, card_no):
        super(InvalidCardNoError, self).__init__("Invalid card number [card_no={0}].".format(card_no))


class TryToBindCreditCardToPrivateAccountError(BankcardError):
    def __init__(self, card_no):
        message = "The bank card must be a Debit Card if it was added as private account [card_no={0}].".format(
            card_no)
        super(TryToBindCreditCardToPrivateAccountError, self).__init__(message)
