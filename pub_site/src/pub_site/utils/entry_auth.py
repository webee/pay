# coding=utf-8
from __future__ import unicode_literals
from functools import wraps
from flask import request
import urlparse
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


def limit_referrer(netlocs):
    def do_limit(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                referrer = request.referrer
                parts = urlparse.urlparse(referrer)
                if parts.netloc in netlocs:
                    return f(*args, **kwargs)
            except Exception as e:
                logger.exception(e)
            return "非法请求"
        return wrapper
    return do_limit
