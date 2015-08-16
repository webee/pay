# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from api_x.core import ZytCoreError


class TransactionApiError(ZytCoreError):
    def __init__(self, message):
        super(TransactionApiError, self).__init__(message)


class InvalidSignError(TransactionApiError):
    def __init__(self, sign_type, signed_data):
        message = "Sign verification failed [SignType={0}, SignedData={1}].".format(sign_type, signed_data)
        super(InvalidSignError, self).__init__(message)


class UnExpectedResponseError(TransactionApiError):
    def __init__(self, status_code, content):
        message = "Api didn't response as expected [StatusCode={0}, Content={1}].".format(status_code, content)
        super(UnExpectedResponseError, self).__init__(message)


class RequestFailedError(TransactionApiError):
    def __init__(self, return_code, return_msg):
        message = "Request failed, because ReturnCode is {0} and Message is {1}.".format(return_code, return_msg)
        super(TransactionApiError, self).__init__(message)


class DictParsingError(TransactionApiError):
    def __init__(self, raw_data):
        message = "Data [{0}] must be a dict.".format(raw_data)
        super(TransactionApiError, self).__init__(message)
