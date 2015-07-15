# -*- coding: utf-8 -*-
from .lianlian_api import request
from .lianlian_config import config


def query_order():
    # TODO:

    params = {
        'platform': config.platform,
        'oid_partner': config.oid_partner,
    }

    return request(config.order.url, params)
