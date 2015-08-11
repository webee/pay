# coding=utf-8
from __future__ import unicode_literals
from datetime import timedelta

from .app import celery


if not celery:
    raise ValueError("Celery isn't initialized yet")


@celery.task(ignore_result=True)
def withdraw_notify(url, params, count=1):
    _notify_client(withdraw_notify, url, params, count)


@celery.task
def add(x, y):
    return x + y


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
