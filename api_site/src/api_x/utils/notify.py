# -*- coding: utf-8 -*-
import requests
import json
from tools.mylog import get_logger


logger = get_logger(__name__)


def notify_client(url, params):
    try:
        resp = requests.post(url, params)
        logger.info("notify url [{0}] status_code [{1}]".format(url, resp.status_code))
        if resp.status_code != 200:
            logger.warn('notify [{0}, {1}] failed.'.format(url, json.dumps(params)))
            return False
    except Exception as e:
        logger.exception(e)
        return False

    return True
