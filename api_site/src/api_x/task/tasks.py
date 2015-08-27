# coding=utf-8
from __future__ import unicode_literals

from celery import Celery
from api_x.utils.notify import notify_client
from datetime import timedelta, datetime
import time


app = Celery('pay_api')


@app.task
def test_job():
    import random
    count = random.randint(1, 20)
    for i in range(count):
        _ = test_task.apply_async(args=[i], queue='test_task', routing_key='test_task')

    return count


@app.task(ignore_result=True, queue='test_task', routing_key='test_task')
def test_task(i):
    print(i)


@app.task(queue='test_task', routing_key='test_task')
def add(a, b):
    return a + b


@app.task(ignore_result=True, queue='pay_notify', routing_key='pay_notify')
def pay_notify(url, params, next_time=None, count=1, max_times=30, interval=0.5):
    do_notify_client(pay_notify, url, params, next_time, count, max_times, interval)


@app.task(ignore_result=True, queue='withdraw_notify', routing_key='withdraw_notify')
def withdraw_notify(url, params, next_time=None, count=1, max_times=30, interval=2):
    do_notify_client(withdraw_notify, url, params, next_time, count, max_times, interval)


@app.task(ignore_result=True, queue='refund_notify', routing_key='refund_notify')
def refund_notify(url, params, next_time=None, count=1, max_times=30, interval=1):
    do_notify_client(refund_notify, url, params, next_time, count, max_times, interval)


def do_notify_client(task, url, params, next_time, count, max_times=30, interval=2):
    # max execute 30 times.
    if count > max_times:
        return

    now = datetime.now()
    if next_time is not None and now < next_time:
        time.sleep(0.5)
        task.delay(url, params, next_time, count=count, max_times=max_times, interval=interval)
        return

    if not notify_client(url, params):
        # retry every two minutes.
        next_time = now + timedelta(minutes=interval)
        task.delay(url, params, next_time, count + 1, max_times=max_times, interval=interval)
