# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.evas.constant import NotifyRespTypes

_methods = {}


def _register_method(t):
    def register(f):
        _methods[t] = f
        return f

    return register


@_register_method(NotifyRespTypes.SUCCEED)
def succeed():
    return 'success'


@_register_method(NotifyRespTypes.FAILED)
def failed():
    return 'failed'


@_register_method(NotifyRespTypes.DUPLICATE)
def duplicate():
    """重复通知, 不再通知"""
    return succeed()


@_register_method(NotifyRespTypes.BAD)
def bad():
    return succeed()


@_register_method(NotifyRespTypes.MISS)
def miss():
    """没有处理, 期待下次发送处理"""
    return failed()


@_register_method(NotifyRespTypes.WRONG)
def wrong():
    """返回数据有问题"""
    return failed()


@_register_method(NotifyRespTypes.RETRY)
def retry():
    return failed()


def response(t, *args, **kwargs):
    return _methods[t](*args, **kwargs)
