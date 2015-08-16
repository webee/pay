# coding=utf-8
from __future__ import unicode_literals

from functools import wraps

from flask import request
from ..api_x.zyt.evas.lianlian_pay.api_access import parse_and_verify_request_data
from ..error import *
from . import notification


def parse_and_verify(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            verified_data = parse_and_verify_request_data(request.values, request.data)
            request.__dict__['verified_data'] = verified_data
        except (DictParsingError, InvalidSignError):
            return notification.is_invalid()
        return f(*args, **kwargs)
    return wrapper
