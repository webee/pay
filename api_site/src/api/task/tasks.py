# coding=utf-8
from __future__ import unicode_literals
from datetime import timedelta
from api.util.notify import notify_client

from .app import celery


if not celery:
    raise ValueError("Celery isn't initialized yet")


@celery.task
def withdraw_notify(url, params, count=1):
    _send_notification_to_client(withdraw_notify, url, params, count)


@celery.task
def refund_notify(url, params, count=1):
    _send_notification_to_client(withdraw_notify, url, params, count)


def _send_notification_to_client(task, url, params, count):
    # max execute 30 times.
    if count > 30:
        return

    if not notify_client(url, params):
        # retry every two minutes.
        next_time = timedelta(minutes=2)
        task.delay(url, params, next_time, count=count + 1)
