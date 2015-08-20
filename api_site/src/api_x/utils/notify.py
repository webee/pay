# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


def notify_client(url, params, methods=['post']):
    logger.info("notify [{0}]: {1}".format(url, params))
    if url:
        for method in methods:
            try:
                resp = requests.request(method, url, data=params)
                logger.info("notify url {0} [{1}] status_code [{2}]".format(method, url, resp.status_code))
                if resp.status_code == 200:
                    logger.info('return: {0}'.format(resp.content))
                    data = resp.json()
                    if data['code'] == 0:
                        return True
                else:
                    logger.warning('return {0}'.format(resp.content))
            except Exception as e:
                logger.exception(e)

    return False
