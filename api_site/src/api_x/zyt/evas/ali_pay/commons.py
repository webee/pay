# coding=utf-8
from __future__ import unicode_literals

from api_x.config import ali_pay
from pytoolbox.util.urls import build_url
from pytoolbox.util.log import get_logger
from api_x.zyt.evas.error import InvalidSignError
import requests

logger = get_logger(__name__)


def generate_absolute_url(path):
    return ali_pay.ROOT_URL + path


def notify_verify(notify_id):
    if notify_id is None:
        return True
    params = {
        'service': ali_pay.Service.NOTIFY_VERIFY,
        'partner': ali_pay.PID,
        'notify_id': notify_id
    }
    url = build_url(ali_pay.GATEWAY_URL, **params)
    try:
        req = requests.get(url)
        res = req.text
        ok = res == 'true'
        if not ok:
            logger.warn('notify verify: [{0}]'.format(res))
        return ok
    except Exception as e:
        logger.warn(e.message)
    return False


def verify_sign(data, do_raise=False):
    from . import signer

    if 'sign_type' in data and signer.verify(data, data['sign_type']):
        return True

    if do_raise:
        raise InvalidSignError(data.get('sign_type'), data)
    return False


def is_success_status(status):
    return status in {ali_pay.TradeStatus.TRADE_SUCCESS, ali_pay.TradeStatus.TRADE_FINISHED}

