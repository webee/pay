# coding=utf-8
from __future__ import unicode_literals


class EvasError(Exception):
    def __init__(self, message):
        if isinstance(message, unicode):
            message = message.encode('utf-8')
        super(EvasError, self).__init__(message)
