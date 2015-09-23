# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.vas.notify import get_pay_notify_handle, NotifyType, get_refund_notify_handle
from .bookkeep import bookkeeping, EventType
from pytoolbox.util.log import get_logger
from api_x.zyt.biz.models import TransactionType
from api_x.config import etc as config

NAME = 'ZYT'


logger = get_logger(__name__)


def pay(source, sn, channel=None):
    if source != TransactionType.PAYMENT:
        # 自游通支付只支持支付，不支持充值等方式
        raise Exception("自游通支付暂只支持支付")

    is_success = _do_pay(source, sn)

    if channel in [config.Biz.Channel.APP, config.Biz.Channel.API]:
        return {"is_success": is_success}

    # web请求
    sync_handle = get_pay_notify_handle(source, NotifyType.Pay.SYNC)
    return sync_handle(is_success, sn, NAME, sn, None)


def _do_pay(source, sn):
    # 通知payer扣钱
    try:
        paid_out_handle = get_pay_notify_handle(source, NotifyType.Pay.PAID_OUT)
        paid_out_handle(NAME, sn)
        is_success = True
    except Exception as e:
        logger.exception(e)
        is_success = False

    # 通知payee到账
    async_handle = get_pay_notify_handle(source, NotifyType.Pay.ASYNC)
    async_handle(is_success, sn, NAME, sn, None)

    return is_success


def refund(source, sn):
    # 通知payee扣钱
    async_handle = get_refund_notify_handle(source, NotifyType.Refund.ASYNC)
    async_handle(True, sn, NAME, sn, None)

    # 通知payer加钱
    refund_in_handle = get_refund_notify_handle(source, NotifyType.Refund.REFUND_IN)
    refund_in_handle(NAME, sn)

    return True
