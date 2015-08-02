# -*- coding: utf-8 -*-
from .lianlian_api import request
from .conf import config, zyt_url
from .util import datetime_to_str, generate_url


def refund(refund_id, refunded_on, amount, paybill_id):
    params = {
        'oid_partner': config.oid_partner,
        'sign_type': config.sign_type_md5,
        'no_refund': str(refund_id),
        'dt_refund': datetime_to_str(refunded_on),
        'money_refund': str(amount),
        'oid_paybill': paybill_id,
        'notify_url': generate_url(zyt_url.refund_notify, refund_id)
    }
    return request(config.url_refund, params)
