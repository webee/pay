# coding=utf-8
from kombu import Exchange, Queue

BROKER_URL = 'amqp://lvye_pay:p@55word@127.0.0.1:5672/lvye_pay'
CELERY_RESULT_BACKEND = 'amqp://lvye_pay:p@55word@127.0.0.1:5672/lvye_pay'

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
    Queue('test_task', Exchange('test_task', 'direct'), routing_key='test_task'),
    Queue('pay_notify', Exchange('pay_notify', 'direct'), routing_key='pay_notify'),
    Queue('prepaid_notify', Exchange('prepaid_notify', 'direct'), routing_key='prepaid_notify'),
    Queue('withdraw_notify', Exchange('withdraw_notify', 'direct'), routing_key='withdraw_notify'),
    Queue('refund_notify', Exchange('refund_notify', 'direct'), routing_key='refund_notify'),
)

CELERY_ROUTES = {
    'api_x.task.tasks.test_task': {'queue': 'test_task', 'routing_key': 'test_task'},
    'api_x.task.tasks.pay_notify': {'queue': 'pay_notify', 'routing_key': 'pay_notify'},
    'api_x.task.tasks.prepaid_notify': {'queue': 'prepaid_notify', 'routing_key': 'prepaid_notify'},
    'api_x.task.tasks.withdraw_notify': {'queue': 'withdraw_notify', 'routing_key': 'withdraw_notify'},
    'api_x.task.tasks.refund_notify': {'queue': 'refund_notify', 'routing_key': 'refund_notify'},
}

from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    'test_job-E0.5d': {
        'task': 'api_x.task.tasks.test_job',
        'schedule': timedelta(days=0.5),
        'kwargs': {},
        'relative': True,
        'options': {'queue': 'celery_periodic'}
    },
}

CELERY_TIMEZONE = 'UTC'

CELERY_EVENT_QUEUE_TTL = 15
CELERY_EVENT_QUEUE_EXPIRES = 600
