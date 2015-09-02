# coding=utf-8
import os
from celery import Celery

celery = Celery('pay_api')

from . import tasks


def init_celery_app(app, config, flask_app=None):
    app.config_from_object(config)
    app.conf.update(os.environ)

    if flask_app is not None:
        BaseTask = app.Task

        class ContextTask(BaseTask):
            abstract = True

            def __call__(self, *args, **kwargs):
                with flask_app.app_context():
                    return BaseTask.__call__(self, *args, **kwargs)

        app.Task = ContextTask

    return app
