# -*- coding: utf-8 -*-
from .lianlian_api import request
from .lianlian_config import config
from .util import datetime_to_str, generate_url


def refund(refund_id, refunded_on, amount, paybill_id):
    notification_url = _generate_refund_notification_url(refund_id)

    params = {
        'oid_partner': config.oid_partner,
        'sign_type': config.sign_type.MD5,
        'no_refund': str(refund_id),
        'dt_refund': datetime_to_str(refunded_on),
        'money_refund': str(amount),
        'oid_paybill': paybill_id,
        'notify_url': notification_url
    }
    return request(config.refund.url, params)


def _generate_refund_notification_url(id):
    return generate_url(config.payment.notify_url, id)

