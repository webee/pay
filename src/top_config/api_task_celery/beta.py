# coding=utf-8
BROKER_URL = 'amqp://lvye_pay:p@55word@192.168.12.126:5672/lvye_pay'
CELERY_RESULT_BACKEND = 'amqp://lvye_pay:p@55word@192.168.12.126:5672/lvye_pay'


from datetime import timedelta
CELERYBEAT_SCHEDULE = {
    'confirm_to_pay_all-E10m': {
        'task': 'api.task.pay_tasks.confirm_to_pay_all',
        'schedule': timedelta(seconds=30),
        'kwargs': {},
        'relative': True,
        'options': {'queue': 'celery_periodic'}
    },

    'settle_all_cash_balance-E0.5d': {
        'task': 'api.task.pay_tasks.settle_all_cash_balance',
        'schedule': timedelta(seconds=20),
        'kwargs': {},
        'relative': True,
        'options': {'queue': 'celery_periodic'}
    },
}
