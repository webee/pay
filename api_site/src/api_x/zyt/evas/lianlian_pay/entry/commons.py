# coding=utf-8
from __future__ import unicode_literals

from functools import wraps

from flask import request
from . import notify_response
from ..api_access import parse_and_verify_request_data
from ..error import *


def parse_and_verify(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # TODO: 应该所有的回调都是POST, GET是在『支付失败』的情况出现
        if request.method != "GET":
            try:
                if request.values.get('res_data'):
                    data = request.values.get('res_data')
                    verified_data = parse_and_verify_request_data(None, data)
                else:
                    verified_data = parse_and_verify_request_data(request.values, request.data)
            except (DictParsingError, InvalidSignError):
                return notify_response.wrong()
            request.__dict__['verified_data'] = verified_data
        return f(*args, **kwargs)
    return wrapper
