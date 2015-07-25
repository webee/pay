# -*- coding: utf-8 -*-
from .lianlian_api import request
from .config import lianlian as config
from .util import datetime_to_str, generate_url


def refund(refund_id, refunded_on, amount, paybill_id):
    params = {
        'oid_partner': config.OID_PARTNER,
        'sign_type': config.SignType.MD5,
        'no_refund': str(refund_id),
        'dt_refund': datetime_to_str(refunded_on),
        'money_refund': str(amount),
        'oid_paybill': paybill_id,
        'notify_url': generate_url(config.Refund.NOTIFY_URL, refund_id)
    }
    return request(config.Refund.URL, params)
