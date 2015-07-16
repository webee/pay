# coding=utf-8
from __future__ import unicode_literals
import os
from tasks import make_celery_app


app = make_celery_app('pay', os.getenv('TASK_CONFIG', 'tasks.config'))


@app.task(ignore_result=True)
def test(*args, **kwargs):
    pass
