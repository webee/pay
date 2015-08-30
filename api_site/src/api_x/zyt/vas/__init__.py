# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.vas.notify import get_pay_notify_handle, NotifyType, get_refund_notify_handle
from .bookkeep import bookkeeping, EventType
from pytoolbox.util.log import get_logger

NAME = 'ZYT'


logger = get_logger(__name__)


def pay(source, sn):
    try:
        paid_out_handle = get_pay_notify_handle(source, NotifyType.Pay.PAID_OUT)
        paid_out_handle(sn)
        is_success = True
    except Exception as e:
        logger.exception(e)
        is_success = False

    async_handle = get_pay_notify_handle(source, NotifyType.Pay.ASYNC)
    async_handle(is_success, sn, NAME, sn, None)

    sync_handle = get_pay_notify_handle(source, NotifyType.Pay.SYNC)
    return sync_handle(is_success, sn, NAME, sn, None)


def refund(source, sn):
    async_handle = get_refund_notify_handle(source, NotifyType.Refund.ASYNC)
    async_handle(True, sn, NAME, sn, None)

    refund_in_handle = get_refund_notify_handle(source, NotifyType.Refund.REFUND_IN)
    refund_in_handle(sn)

    return True
