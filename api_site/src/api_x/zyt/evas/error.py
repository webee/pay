# coding=utf-8
from __future__ import unicode_literals


class EvasError(Exception):
    def __init__(self, message):
        message = message.encode('utf-8') if isinstance(message, unicode) else message
        super(EvasError, self).__init__(message)


class ApiError(EvasError):
    def __init__(self, message, data=None):
        super(ApiError, self).__init__(message)
        self.data = data


class InvalidSignError(ApiError):
    def __init__(self, sign_type, signed_data):
        message = "Sign verification failed [SignType={0}, SignedData={1}].".format(sign_type, signed_data)
        super(InvalidSignError, self).__init__(message)


class UnExpectedResponseError(ApiError):
    def __init__(self, status_code, content):
        message = "Api didn't response as expected [StatusCode={0}, Content={1}].".format(status_code, content)
        super(UnExpectedResponseError, self).__init__(message)


class DataParsingError(ApiError):
    def __init__(self, msg):
        message = "data parse error: {0}".format(msg)
        super(ApiError, self).__init__(message)


class DictParsingError(ApiError):
    def __init__(self, raw_data):
        message = "Data [{0}] must be a dict.".format(raw_data)
        super(ApiError, self).__init__(message)


class RefundBalanceInsufficientError(ApiError):
    def __init__(self):
        msg = "refund balance insufficient error."
        super(RefundBalanceInsufficientError, self).__init__(msg)


class DataEncodingError(ApiError):
    def __init__(self, message=None):
        message = message or "encoding error."
        super(ApiError, self).__init__(message)


class RequestFailedError(ApiError):
    def __init__(self, message=None):
        message = message or "request failed."
        super(ApiError, self).__init__(message)


class PaymentTypeNotImplementedError(EvasError):
    def __init__(self, evas, payment_type):
        msg = "payment type [{0}] not implemented by [{1}]".format(payment_type, evas)
        super(EvasError, self).__init__(msg)


class PaymentTypeNotSupportedError(EvasError):
    def __init__(self, evas, payment_type):
        msg = "payment type [{0}] not supported by [{1}]".format(payment_type, evas)
        super(EvasError, self).__init__(msg)
