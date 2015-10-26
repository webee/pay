# coding=utf-8
from __future__ import unicode_literals

from functools import wraps

from flask import request
from . import notify_response
from ..api_access import parse_and_verify_request_data
from ...error import *


def parse_and_verify(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            params = request.view_args
            app = params['app']
            verified_data = parse_and_verify_request_data(app, request.data)
        except (DictParsingError, InvalidSignError):
            return notify_response.wrong()
        request.__dict__['verified_data'] = verified_data
        return f(*args, **kwargs)
    return wrapper
