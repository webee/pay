# coding=utf-8
from datetime import timedelta

BROKER_URL = 'amqp://lvye_pay:p@55word@127.0.0.1:5672/lvye_pay_beta'
CELERY_RESULT_BACKEND = 'amqp://lvye_pay:p@55word@127.0.0.1:5672/lvye_pay_beta'


CELERYBEAT_SCHEDULE = {
    'test_job-E0.5d': {
        'task': 'api_x.task.tasks.test_job',
        'schedule': timedelta(seconds=10),
        'kwargs': {},
        'relative': True,
        'options': {'queue': 'celery_periodic'}
    },
}
