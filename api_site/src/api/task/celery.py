# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import Celery
from api import config


_URL = 'amqp://{2}:{3}@{0}/{1}'.format(config.Celery.HOST, config.Celery.INSTANCE,
                                       config.Celery.USERNAME, config.Celery.PASSWORD)

app = Celery('api.tasks', broker=_URL, backend=_URL, include=['api.task.tasks'])
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600
)


if __name__ == '__main__':
    app.start()
