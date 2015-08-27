# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
from pytoolbox.util.sign import SignType
from pytoolbox.util.log import get_logger
from api_x.zyt.user_mapping.auth import add_sign_for_params
from api_x.utils import response


logger = get_logger(__name__)


def sign_and_return_client_callback(url, channel_name, params, sign_type=SignType.RSA, method='POST'):
    params = add_sign_for_params(channel_name, params, sign_type)
    logger.info("return {0} [{1}] status_code [{2}]".format(method, url, params))
    return response.submit_form(url, params, method)


def sign_and_notify_client(url, params, channel_name, methods=['post'], task=None):
    params = add_sign_for_params(channel_name, params)
    if params and not notify_client(url, params, methods):
        task.apply_async(args=[url, params], countdown=3)


def notify_client(url, params, methods=['post']):
    logger.info("notify [{0}]: {1}".format(url, params))
    if not url:
        return True

    for method in methods:
        try:
            resp = requests.request(method, url, data=params)
            logger.info("notify {0} [{1}] status_code [{2}]".format(method, url, resp.status_code))
            if resp.status_code == 200:
                logger.info('notify response: {0}'.format(resp.content))
                data = resp.json()
                if data['code'] in [0, '0']:
                    return True
            else:
                logger.warning('notify response: {0}'.format(resp.content))
        except Exception as e:
            logger.exception(e)

    return False
