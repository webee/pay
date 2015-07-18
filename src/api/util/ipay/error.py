# -*- coding: utf-8 -*-


class ApiError(Exception):
    def __init__(self, message):
        super(ApiError, self).__init__(message)


class InvalidSignError(ApiError):
    def __init__(self, sign_type, signed_data):
        message = "Sign verification failed [SignType={0}, SignedData={1}]".format(sign_type, signed_data)
        super(InvalidSignError, self).__init__(message)