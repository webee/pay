# -*- coding: utf-8 -*-
from .lianlian_api import request
from .config import lianlian as config


def query_order():
    # TODO:

    params = {
        'platform': config.PLATFORM,
        'oid_partner': config.OID_PARTNER
    }

    return request(config.Order.URL, params)
