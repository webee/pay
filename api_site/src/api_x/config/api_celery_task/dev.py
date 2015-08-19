# coding=utf-8
from datetime import timedelta


CELERYBEAT_SCHEDULE = {
    'test_job-E0.5d': {
        'task': 'api_x.task.tasks.test_job',
        'schedule': timedelta(seconds=5),
        'kwargs': {},
        'relative': True,
        'options': {'queue': 'celery_periodic'}
    },
}
