# -*- coding: utf-8 -*-
from api.util.uuid import encode_uuid
from .lianlian_api import request
from .lianlian_config import config
from .util import datetime_to_str, generate_notification_url


def refund(refund_id, refunded_on, amount, paybill_id, url_root):
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


def _encode_uuid(refund_id):
    return encode_uuid('%0.8d' % refund_id)


def _generate_refund_notification_url(id):
    return generate_notification_url(config.payment.notify_url, id)

