# -*- coding: utf-8 -*-
from .lianlian_api import request
from .conf import config


def query_order(no_order, dt_order, oid_paybill, type_dc):
    params = {
        'oid_partner': config.oid_partner,
        'sign_type': config.sign_type_md5,
        'no_order': no_order,
        'dt_order': dt_order,
        'oid_paybill': oid_paybill,
        'type_dc': type_dc,
        'query_version': config.order_query_version
    }

    return request(config.url_order_query, params)
