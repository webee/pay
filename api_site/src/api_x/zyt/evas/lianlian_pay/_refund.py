# -*- coding: utf-8 -*-
from .api_access import request
from api_x.zyt.evas.util import datetime_to_str
from api_x.config import lianlian_pay
from pytoolbox.util.sign import SignType


def refund(refund_no, refunded_on, amount, paybill_id, notify_url):
    params = {
        'oid_partner': lianlian_pay.OID_PARTNER,
        'sign_type': SignType.MD5,
        'no_refund': str(refund_no),
        'dt_refund': datetime_to_str(refunded_on),
        'money_refund': str(amount),
        'oid_paybill': paybill_id,
        'notify_url': notify_url
    }
    return request(lianlian_pay.Refund.URL, params)


def is_success_or_fail(status):
    if status == lianlian_pay.Refund.Status.SUCCESS:
        return True
    if status == lianlian_pay.Refund.Status.FAILED:
        return False
    return None


def refund_query(refund_no, refunded_on, oid_refundno=''):
    dt_refund = refunded_on
    if not isinstance(refunded_on, str):
        dt_refund = datetime_to_str(refunded_on)

    params = {
        'oid_partner': lianlian_pay.OID_PARTNER,
        'sign_type': SignType.RSA,
        'no_refund': str(refund_no),
        'dt_refund': dt_refund,
        'oid_refundno': oid_refundno
    }

    return request(lianlian_pay.Refund.QUERY_URL, params)
