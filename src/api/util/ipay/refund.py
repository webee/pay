# -*- coding: utf-8 -*-
from urlparse import urljoin
from api.util.uuid import encode_uuid
from .lianlian_api import request
from .lianlian_config import config
from .util import datetime_to_str


def refund(refund_id, refunded_on, amount, paybill_id, url_root):
    uuid = _encode_uuid(refund_id)
    notification_url = _generate_notification_url(url_root, config.refund.notify_url, uuid)

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


def _generate_notification_url(url_root, relative_url, uuid):
    params = {'uuid': uuid}
    relative_url = relative_url.format(**params)
    return urljoin(url_root, relative_url)

