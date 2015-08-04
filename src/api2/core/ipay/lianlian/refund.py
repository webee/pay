# -*- coding: utf-8 -*-
from .api import request
from . import config
from .util import datetime_to_str


def refund(refund_id, refunded_on, amount, paybill_id, notify_url):
    params = {
        'oid_partner': config.oid_partner,
        'sign_type': config.sign_type_md5,
        'no_refund': str(refund_id),
        'dt_refund': datetime_to_str(refunded_on),
        'money_refund': str(amount),
        'oid_paybill': paybill_id,
        'notify_url': notify_url
    }
    return request(config.url_refund, params)
