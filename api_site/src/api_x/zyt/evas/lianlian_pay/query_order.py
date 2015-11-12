# -*- coding: utf-8 -*-
from .api_access import request
from api_x.config import lianlian_pay
from pytoolbox.util.sign import SignType
from .commons import get_pure_result


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

    # FIXME: 处理成功时无法通过验证的问题。
    res = request(lianlian_pay.OrderQuery.URL, params, pass_verify=True)
    return get_pure_result(res)
