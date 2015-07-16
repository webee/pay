# coding=utf-8
from kombu import Exchange, Queue
import os

BROKER_URL = 'redis://127.0.0.1:6379/1'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/1'

BROKER_POOL_LIMIT = 48

CELERY_MAX_CACHED_RESULTS = 1000
CELERY_TASK_RESULT_EXPIRES = 3600

CELERYD_PREFETCH_MULTIPLIER = 8
CELERYD_MAX_TASKS_PER_CHILD = 10000
CELERYD_TASK_TIME_LIMIT = 36

CELERY_DEFAULT_QUEUE = 'celery'
CELERY_QUEUES = (
    Queue('celery', Exchange('celery', 'direct'), routing_key='celery'),
    Queue('op_hist', Exchange('op_hist', 'direct'), routing_key='op_hist'),
    Queue('celery_periodic', Exchange('celery_periodic', 'direct'), routing_key='celery_periodic'),
)

CELERY_ROUTES = {
    'tasks.img_score_tasks.process_op_hist': {'queue': 'op_hist', 'routing_key': 'op_hist'},
}

from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    'consume_op_history-E60s': {
        'task': 'tasks.img_score_tasks.consume_op_history',
        'schedule': timedelta(seconds=1*60),
        'kwargs': {'def_ahead': 30, 'd': 10, 'use_id': True, 'use_id': True},
        'relative': True,
        'options': {'queue': 'celery_periodic'}
    },
    'consume_qhimgs-E0.5d': {
        'task': 'tasks.img_score_tasks.consume_qhimgs',
        'schedule': timedelta(days=0.5),
        'relative': True,
        'options': {'queue': 'celery_periodic'}
    },
}

CELERY_TIMEZONE = 'UTC'


CELERY_EVENT_QUEUE_TTL = 15
CELERY_EVENT_QUEUE_EXPIRES = 600

DEF_TYPE = int(os.environ.get('DEF_TYPE', '0'))
DEF_CLF_TYPE = os.environ.get('DEF_CLF_TYPE', 'x')
DEF_DATA_NAME = os.environ.get('DEF_DATA_NAME', 'selected')
DEF_MODEL_NAME = os.environ.get('DEF_MODEL_NAME', 'svm')
