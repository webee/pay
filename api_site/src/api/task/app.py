# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import Celery, Task as TaskBase
from api import config


celery = None

def make_celery(app):
    global celery

    rabbitmq_url = 'amqp://{2}:{3}@{0}/{1}'.format(config.Celery.HOST, config.Celery.INSTANCE,
                                                   config.Celery.USERNAME, config.Celery.PASSWORD)
    celery = Celery(app.import_name, broker=rabbitmq_url)
    celery.conf.update(
        CELERY_TASK_RESULT_EXPIRES=3600,
    )

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super(ContextTask, self).__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


