# coding=utf-8
from __future__ import unicode_literals

from functools import wraps

from flask import request
from pytoolbox.util.log import get_logger
from . import notify_response
from ..api_access import parse_and_verify_request_data
from ...error import *


logger = get_logger(__name__)


def parse_and_verify(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # TODO: 应该所有的回调都是POST, GET是在『支付失败』的情况出现
        logger.info("requested {0}: {1}, {2}".format(request.url, request.values, request.data))
        if request.method != "GET":
            try:
                if request.values.get('res_data'):
                    # 此res_data为wap支付的同步返回参数
                    data = request.values.get('res_data')
                    verified_data = parse_and_verify_request_data(None, data)
                else:
                    verified_data = parse_and_verify_request_data(request.values, request.data)
            except (DictParsingError, InvalidSignError):
                return notify_response.wrong()
            request.__dict__['verified_data'] = verified_data
        return f(*args, **kwargs)
    return wrapper
