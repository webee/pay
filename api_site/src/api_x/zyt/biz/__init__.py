# coding=utf-8
from api_x.constant import TransactionType
from .payment import handle_payment_result, handle_payment_notify
from .models import VirtualAccountSystem


def init_test_pay_notify_handles():
    from api_x.zyt.evas.test_pay.constant import BizType, NotifyType
    from api_x.zyt.evas.test_pay.notify import register_notify_handle

    # payment
    register_notify_handle(TransactionType.PAYMENT, BizType.PAY, NotifyType.SYNC, handle_payment_result)
    register_notify_handle(TransactionType.PAYMENT, BizType.PAY, NotifyType.ASYNC, handle_payment_notify)


def init_lianlian_pay_notify_handles():
    pass


def init_register_notify_handles():
    init_test_pay_notify_handles()
    init_lianlian_pay_notify_handles()