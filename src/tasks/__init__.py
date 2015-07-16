# coding=utf-8
import os
from celery import Celery


def make_celery_app(name, config):
    app = Celery(name)
    app.config_from_object(config)
    app.conf.update(os.environ)

    return app
