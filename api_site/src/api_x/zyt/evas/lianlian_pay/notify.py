# coding=utf-8
from __future__ import unicode_literals

from .constant import BizType, NotifyType

_all_handles = {}


def _register_notify_handle(source, biz_type, notify_type, handle):
    """
    注册通知处理器
    :param source: 来源，比如：支付，充值，退款，提现
    :param biz_type: 连连提供的业务接口类型：支付，退款，代付
    :param notify_type: 同步，异步
    :param handle: 处理函数
    :return:
    """
    source_handles = _all_handles.setdefault(source, {})
    handles = source_handles.setdefault(biz_type, {})
    handles[notify_type] = handle


def _get_notify_handle(source, biz_type, notify_type):
    return _all_handles[source][biz_type][notify_type]


def register_handle(source, biz_type, notify_type):
    def wrap(handle):
        _register_notify_handle(source, biz_type, notify_type, handle)
        return handle
    return wrap


def register_pay_notify_handle(source, notify_type, handle):
    if notify_type not in [NotifyType.Pay.SYNC, NotifyType.Pay.ASYNC]:
        raise ValueError('notify_type: [{0}] not supported.'.format(notify_type))
    _register_notify_handle(source, BizType.PAY, notify_type, handle)


def get_pay_notify_handle(refund_source, notify_type):
    return _get_notify_handle(refund_source, BizType.PAY, notify_type)


def register_refund_notify_handle(source, handle):
    _register_notify_handle(source, BizType.REFUND, NotifyType.Refund.ASYNC, handle)


def get_refund_notify_handle(refund_source):
    return _get_notify_handle(refund_source, BizType.REFUND, NotifyType.Refund.ASYNC)


def register_pay_to_bankcard_notify_handle(source, handle):
    _register_notify_handle(source, BizType.PAY_TO_BANK, NotifyType.Refund.ASYNC, handle)


def get_pay_to_bankcard_notify_handle(source):
    return _get_notify_handle(source, BizType.PAY_TO_BANK, NotifyType.Refund.ASYNC)
