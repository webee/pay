# -*- coding: utf-8 -*-
from .lianlian_api import request
from .config import lianlian as config


def query_order(no_order, dt_order, oid_paybill, type_dc):
    params = {
        'oid_partner': config.OID_PARTNER,
        'sign_type': config.SignType.MD5,
        'no_order': no_order,
        'dt_order': dt_order,
        'oid_paybill': oid_paybill,
        'type_dc': type_dc,
        'query_version': config.Order.QUERY_VERSION
    }

    return request(config.Order.URL, params)
