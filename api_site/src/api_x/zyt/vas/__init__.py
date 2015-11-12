# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.vas.notify import get_pay_notify_handle, NotifyType, get_refund_notify_handle
from .bookkeep import bookkeeping, EventType
from pytoolbox.util.log import get_logger
from api_x.config import zyt_pay as config
from .user import get_account_user
from ..evas.error import PaymentTypeNotImplementedError, PaymentTypeNotSupportedError

NAME = 'ZYT'


logger = get_logger(__name__)


def payment_param(payment_type, source, sn):
    from .payment import pay_param
    from api_x.zyt.biz.models import TransactionType
    if source != TransactionType.PAYMENT:
        # 自游通支付只支持支付，不支持充值等方式
        raise Exception("自游通支付暂只支持支付".encode('utf-8'))

    if payment_type == config.PaymentType.WEB:
        return pay_param(sn)
    elif payment_type == config.PaymentType.APP:
        raise PaymentTypeNotImplementedError(NAME, payment_type)
    else:
        raise PaymentTypeNotSupportedError(NAME, payment_type)


def pay(source, sn, payer_id, amount):
    from api_x.zyt.biz.models import TransactionType
    if source != TransactionType.PAYMENT:
        # 自游通支付只支持支付，不支持充值等方式
        raise Exception("自游通余额付款暂只支持支付".encode('utf-8'))

    payer = get_account_user(payer_id)
    if payer is None:
        raise Exception("payer user [{0}] not exists.".format(payer_id))

    return _do_pay(source, sn, payer_id, amount)


def _do_pay(source, sn, payer_id, amount):
    def notify_payee(is_success):
        # 通知payee到账
        async_handle = get_pay_notify_handle(source, NotifyType.Pay.ASYNC)
        async_handle(is_success, sn, NAME, sn, amount, None)
        # TODO: 在失败的情况下，添加异步任务

    # 通知payer扣钱
    try:
        paid_out_handle = get_pay_notify_handle(source, NotifyType.Pay.PAID_OUT)
        paid_out_handle(NAME, sn, payer_id, amount, notify_handle=notify_payee)
        return True
    except Exception as e:
        logger.exception(e)
        return False


def refund(source, sn):
    def notify_payee(is_success):
        # 通知payee扣钱
        async_handle = get_refund_notify_handle(source, NotifyType.Refund.ASYNC)
        async_handle(is_success, sn, NAME, sn, None)

    # 通知payer加钱
    try:
        refund_in_handle = get_refund_notify_handle(source, NotifyType.Refund.REFUND_IN)
        refund_in_handle(NAME, sn, notify_handle=notify_payee)
        return True
    except Exception as e:
        logger.exception(e)
        return False
