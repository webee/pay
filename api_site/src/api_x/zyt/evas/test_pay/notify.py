# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.evas.test_pay.constant import BizType, NotifyType


_all_handles = {}


def register_notify_handle(source, biz_type, notify_type, handle):
    source_handles = _all_handles.setdefault(source, {})
    handles = source_handles.setdefault(biz_type, {})
    handles[notify_type] = handle


def get_notify_handle(source, biz_type, notify_type):
    return _all_handles[source][biz_type][notify_type]


def register_handle(source, biz_type, notify_type):
    def wrap(handle):
        register_notify_handle(source, biz_type, notify_type, handle)
        return handle
    return wrap


def get_refund_notify_handle(source):
    return get_notify_handle(source, BizType.REFUND, NotifyType.ASYNC)
