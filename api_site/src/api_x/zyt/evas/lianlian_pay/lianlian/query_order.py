# -*- coding: utf-8 -*-
from .api_access import request
from api_x import config


def query_order(no_order):
    params = {
        'oid_partner': config.LianLianPay.OID_PARTNER,
        'sign_type': config.LianLianPay.Sign.MD5_TYPE,
        'no_order': no_order,
        'dt_order': '',
        'oid_paybill': '',
        'type_dc': config.LianLianPay.OrderQuery.PAY_TYPEDC,
        'query_version': config.LianLianPay.OrderQuery.VERSION
    }

    return request(config.LianLianPay.OrderQuery.URL, params)
