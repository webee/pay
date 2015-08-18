# coding=utf-8
from api_x.constant import TransactionType
from .payment import handle_payment_result, handle_payment_notify
from .refund import handle_refund_notify
from .models import VirtualAccountSystem


def init_test_pay_notify_handles():
    from api_x.zyt.evas.test_pay.constant import BizType, NotifyType
    from api_x.zyt.evas.test_pay.notify import register_notify_handle

    # payment
    register_notify_handle(TransactionType.PAYMENT, BizType.PAY, NotifyType.SYNC, handle_payment_result)
    register_notify_handle(TransactionType.PAYMENT, BizType.PAY, NotifyType.ASYNC, handle_payment_notify)

    # refund
    register_notify_handle(TransactionType.REFUND, BizType.REFUND, NotifyType.ASYNC, handle_refund_notify)


def init_lianlian_pay_notify_handles():
    from api_x.zyt.evas.lianlian_pay.constant import NotifyType
    from api_x.zyt.evas.lianlian_pay.notify import register_pay_notify_handle, register_refund_notify_handle

    # payment
    register_pay_notify_handle(TransactionType.PAYMENT, NotifyType.Pay.SYNC, handle_payment_result)
    register_pay_notify_handle(TransactionType.PAYMENT, NotifyType.Pay.ASYNC, handle_payment_notify)

    # refund
    register_refund_notify_handle(TransactionType.REFUND, handle_refund_notify)


def init_register_notify_handles():
    init_test_pay_notify_handles()
    init_lianlian_pay_notify_handles()
