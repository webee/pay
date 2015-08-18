# -*- coding: utf-8 -*-
from .api_access import request
from .util import datetime_to_str
from api_x.config import lianlian_pay


def refund(refund_no, refunded_on, amount, paybill_id, notify_url):
    params = {
        'oid_partner': lianlian_pay.OID_PARTNER,
        'sign_type': lianlian_pay.SignType.MD5,
        'no_refund': str(refund_no),
        'dt_refund': datetime_to_str(refunded_on),
        'money_refund': str(amount),
        'oid_paybill': paybill_id,
        'notify_url': notify_url
    }
    return request(lianlian_pay.Refund.URL, params)


def is_success_status(status):
    return status == lianlian_pay.Refund.Status.SUCCESS
