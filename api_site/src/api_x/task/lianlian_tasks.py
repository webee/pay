# coding=utf-8
from __future__ import unicode_literals

from . import celery


@celery.task(ignore_result=True, queue='refund_notify', routing_key='refund_notify')
def query_refund_notify(*args, **kwargs):
    """在请求Refund之后进行主动查询结果，走到成功或者失败为止"""
    pass
