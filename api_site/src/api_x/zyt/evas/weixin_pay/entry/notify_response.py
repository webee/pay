# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.evas.constant import NotifyRespTypes
from ..api_access import response_xml


_methods = {}


def _register_method(t):
    def register(f):
        _methods[t] = f
        return f

    return register


@_register_method(NotifyRespTypes.SUCCEED)
def succeed():
    return response_xml({'return_code': 'SUCCESS'})


@_register_method(NotifyRespTypes.FAILED)
def failed(msg='FAIL'):
    return response_xml({'return_code': 'FAIL', 'return_msg': msg})


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
    return failed('MISS')


@_register_method(NotifyRespTypes.WRONG)
def wrong():
    """返回数据有问题"""
    return failed('WRONG')


@_register_method(NotifyRespTypes.RETRY)
def retry():
    return failed('RETRY')


def response(t, *args, **kwargs):
    return _methods[t](*args, **kwargs)
