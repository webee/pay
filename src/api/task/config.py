# coding=utf-8
from kombu import Exchange, Queue

BROKER_URL = 'amqp://lvye_pay:p@55word@192.168.12.126:5672/lvye_pay'
CELERY_RESULT_BACKEND = 'amqp://lvye_pay:p@55word@192.168.12.126:5672/lvye_pay'

BROKER_POOL_LIMIT = 12

CELERY_MAX_CACHED_RESULTS = 1000
CELERY_TASK_RESULT_EXPIRES = 3600

CELERYD_PREFETCH_MULTIPLIER = 8
CELERYD_MAX_TASKS_PER_CHILD = 1000
CELERYD_TASK_TIME_LIMIT = 600

CELERY_DEFAULT_QUEUE = 'celery'
CELERY_QUEUES = (
    Queue('celery', Exchange('celery', 'direct'), routing_key='celery'),
    Queue('celery_periodic', Exchange('celery_periodic', 'direct'), routing_key='celery_periodic'),
    Queue('confirm_pay', Exchange('confirm_pay', 'direct'), routing_key='confirm_pay'),
    Queue('settle_cash_balance', Exchange('settle_cash_balance', 'direct'), routing_key='settle_cash_balance'),
)

CELERY_ROUTES = {
    'api.task.pay_tasks.confirm_pay': {'queue': 'confirm_pay', 'routing_key': 'confirm_pay'},
    'api.task.pay_tasks.settle_user_cash_balance': {'queue': 'settle_cash_balance', 'routing_key': 'settle_cash_balance'},
}

from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    'confirm_to_pay_all-E10m': {
        'task': 'api.task.pay_tasks.confirm_to_pay_all',
        'schedule': timedelta(minutes=10),
        'kwargs': {},
        'relative': True,
        'options': {'queue': 'celery_periodic'}
    },

    'settle_all_cash_balance-E0.5d': {
        'task': 'api.task.pay_tasks.settle_all_cash_balance',
        'schedule': timedelta(seconds=5),
        'kwargs': {},
        'relative': True,
        'options': {'queue': 'celery_periodic'}
    },
}

CELERY_TIMEZONE = 'UTC'

CELERY_EVENT_QUEUE_TTL = 15
CELERY_EVENT_QUEUE_EXPIRES = 600
