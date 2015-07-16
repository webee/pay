# coding=utf-8
from __future__ import unicode_literals
import os
from celery_proj import make_celery_app


app = make_celery_app('pay', os.getenv('TASK_CONFIG', 'celery_proj.config'))


@app.task(ignore_result=True)
def test(*args, **kwargs):
    pass
