# -*- coding: utf-8 -*-
import requests
import json
from pytoolbox.util.log import get_logger


_logger = get_logger(__name__)


def notify_client(url, params):
    try:
        resp = requests.post(url, params)
        _logger.info("notify url [{0}] status_code [{1}]".format(url, resp.status_code))
        if resp.status_code != 200:
            _logger.warn('notify [{0}, {1}] failed.'.format(url, json.dumps(params)))
            return False
    except:
        _logger.warn('exception on notifying')
        return False

    return True
