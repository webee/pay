# -*- coding: utf-8 -*-
from .api import request
from . import config


def query_order(no_order):
    params = {
        'oid_partner': config.oid_partner,
        'sign_type': config.sign_type_md5,
        'no_order': no_order,
        'dt_order': '',
        'oid_paybill': '',
        'type_dc': config.order_typedc_pay,
        'query_version': config.order_query_version
    }

    return request(config.url_order_query, params)
