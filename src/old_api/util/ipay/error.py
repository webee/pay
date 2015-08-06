# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class ApiError(Exception):
    def __init__(self, message):
        super(ApiError, self).__init__(message)


class InvalidSignError(ApiError):
    def __init__(self, sign_type, signed_data):
        message = "Sign verification failed [SignType={0}, SignedData={1}].".format(sign_type, signed_data)
        super(InvalidSignError, self).__init__(message)


class UnExpectedResponseError(ApiError):
    def __init__(self, status_code, content):
        message = "Api didn't response as expected [StatusCode={0}, Content={1}].".format(status_code, content)
        super(UnExpectedResponseError, self).__init__(message)


class RequestFailedError(ApiError):
    def __init__(self, return_code, return_msg):
        message = "Request failed, because ReturnCode is {0} and Message is {1}.".format(return_code, return_msg)
        super(ApiError, self).__init__(message)


class DictParsingError(ApiError):
    def __init__(self, raw_data):
        message = "Data [{0}] mst be a dict.".format(raw_data)
        super(ApiError, self).__init__(message)
