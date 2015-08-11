# coding=utf-8
from __future__ import unicode_literals
from datetime import timedelta

from .celery import app
from pytoolbox.util.log import get_logger


_logger = get_logger(__name__)


@app.task(ignore_result=True, queue='withdraw_notify', routing_key='withdraw_notify')
def withdraw_notify(url, params, count=1):
    _notify_client(withdraw_notify, url, params, count)


def _notify_client(task, url, params, count):
    # max execute 30 times.
    if count > 30:
        return

    if not _send_notification_to_client(url, params):
        # retry every two minutes.
        next_time = timedelta(minutes=2)
        task.delay(url, params, next_time, count=count + 1)


def _send_notification_to_client(url, params):
    import requests, json

    try:
        resp = requests.post(url, params)
        if resp.status_code != 200:
            _logger.warn('notify [{0}, {1}] failed.'.format(url, json.dumps(params)))
            return False
    except:
        return False

    return True
