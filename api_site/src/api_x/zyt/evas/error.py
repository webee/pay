# coding=utf-8


class EvasError(Exception):
    def __init__(self, message):
        super(EvasError, self).__init__(message)
