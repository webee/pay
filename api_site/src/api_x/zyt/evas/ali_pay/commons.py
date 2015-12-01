# coding=utf-8
from __future__ import unicode_literals

from api_x.config import ali_pay
from pytoolbox.util.urls import build_url
from pytoolbox.util.log import get_logger
import requests


logger = get_logger(__name__)


def generate_absolute_url(path):
    return ali_pay.ROOT_URL + path


def notify_verify(notify_id):
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
