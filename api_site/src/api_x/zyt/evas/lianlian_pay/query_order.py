# -*- coding: utf-8 -*-
from .api_access import request
from api_x.config import lianlian_pay
from pytoolbox.util.sign import SignType


def query_order(no_order):
    params = {
        'oid_partner': lianlian_pay.OID_PARTNER,
        'sign_type': SignType.MD5,
        'no_order': no_order,
        'dt_order': '',
        'oid_paybill': '',
        'type_dc': lianlian_pay.OrderQuery.TypeDC.PAY,
        'query_version': lianlian_pay.OrderQuery.VERSION
    }

    return request(lianlian_pay.OrderQuery.URL, params)
