# -*- coding: utf-8 -*-
from .api_access import request
from .util import datetime_to_str
from api import config


def refund(refund_id, refunded_on, amount, paybill_id, notify_url):
    params = {
        'oid_partner': config.LianLianPay.OID_PARTNER,
        'sign_type': config.LianLianPay.Sign.MD5_TYPE,
        'no_refund': str(refund_id),
        'dt_refund': datetime_to_str(refunded_on),
        'money_refund': str(amount),
        'oid_paybill': paybill_id,
        'notify_url': notify_url
    }
    return request(config.LianLianPay.Refund.URL, params)
