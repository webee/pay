# coding=utf-8
from __future__ import unicode_literals

from . import celery
from api_x.utils.notify import notify_client


@celery.task
def test_job():
    import random
    count = random.randint(1, 20)
    for i in range(count):
        _ = test_task.apply_async(args=[i], queue='test_task', routing_key='test_task')

    return count


@celery.task(ignore_result=True, queue='test_task', routing_key='test_task')
def test_task(i):
    print(i)


@celery.task(queue='test_task', routing_key='test_task')
def add(a, b):
    return a + b


@celery.task(ignore_result=True, queue='pay_notify', routing_key='pay_notify')
def pay_notify(url, params, count=1, max_times=30, interval=30):
    do_notify_client(pay_notify, url, params, count, max_times, interval)


@celery.task(ignore_result=True, queue='prepaid_notify', routing_key='prepaid_notify')
def prepaid_notify(url, params, count=1, max_times=30, interval=30):
    do_notify_client(prepaid_notify, url, params, count, max_times, interval)


@celery.task(ignore_result=True, queue='withdraw_notify', routing_key='withdraw_notify')
def withdraw_notify(url, params, count=1, max_times=30, interval=120):
    do_notify_client(withdraw_notify, url, params, count, max_times, interval)


@celery.task(ignore_result=True, queue='refund_notify', routing_key='refund_notify')
def refund_notify(url, params, count=1, max_times=30, interval=60):
    do_notify_client(refund_notify, url, params, count, max_times, interval)


def do_notify_client(notify_task, url, params, count, max_times, interval):
    # max execute 30 times.
    if count > max_times:
        return

    if not notify_client(url, params):
        notify_task.apply_async(args=[url, params],
                                kwargs={'count': count + 1, 'interval': interval, 'max_times': max_times},
                                countdown=interval)
