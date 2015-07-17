# coding=utf-8
from __future__ import unicode_literals
import os
import traceback
from lianlian_mock import make_celery_app
import time
import requests
from tools.mylog import get_logger
from api.util.ipay import transaction

logger = get_logger(__name__)
app = make_celery_app('pay', 'lianlian_mock.%s_config' % os.getenv('SYSTEM_CONFIG'))

__all__ = ['app', 'mock_notify']


@app.task(ignore_result=True)
def mock_notify(url, params, t=1, delay=10):
    time.sleep(delay)

    data = transaction.request(url, params)

    if data['ret']:
        logger.info('notify success: %s' % url)
        return

    logger.warn('notify failed: %s, %s' % (data['code'], data['msg']))

    t += 1
    if t <= 30:
        mock_notify.delay(url, params, t + 1, delay)
