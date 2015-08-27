# coding=utf-8
import os


def init_celery_app(app, config, flask_app=None):
    app.config_from_object(config)
    app.conf.update(os.environ)

    if flask_app is not None:
        class ContextTask(app.Task):
            abstract = True

            def __call__(self, *args, **kwargs):
                with flask_app.app_context():
                    return app.Task.__call__(self, *args, **kwargs)

        app.Task = ContextTask

    return app
