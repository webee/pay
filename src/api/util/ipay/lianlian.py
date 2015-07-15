# coding=utf-8
from __future__ import unicode_literals

from datetime import datetime

from .lianlian_api import request
from .lianlian_config import config


def query_order():
    # TODO:

    params = {
        'platform': config.platform,
        'oid_partner': config.oid_partner,
    }

    return request(config.order.url, params)


def _current_datetime_text():
    now = datetime.now()
    return now.strftime('%Y%m%d%H%M%S')
