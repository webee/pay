# -*- coding: utf-8 -*-
from pytoolbox.util.log import get_logger

_logger = get_logger(__name__)


def try_to_notify_refund_result_client(refund_id):
    # TODO: async_callback_url should be saved in core module?
    pass


def notify_client(url, params):
    import requests, json

    try:
        resp = requests.post(url, params)
        if resp.status_code != 200:
            _logger.warn('notify [{0}, {1}] failed.'.format(url, json.dumps(params)))
            return False
    except:
        return False

    return True
