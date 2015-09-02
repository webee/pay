# coding=utf-8
from __future__ import unicode_literals


_all_handles = {}


def register_query_notify_handle(tx_type, vas_name, handle):
    tx_handles = _all_handles.setdefault(tx_type, {})

    handles = tx_handles.setdefault(vas_name, {})
    handles[vas_name] = handle


def get_query_notify_handle(tx_type, vas_name):
    return _all_handles.get(tx_type, {}).get(vas_name)
