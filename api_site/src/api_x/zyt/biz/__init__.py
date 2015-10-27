# coding=utf-8
from api_x.constant import TransactionType
from .payment import handle_payment_result, handle_payment_notify
from .prepaid import handle_prepaid_result, handle_prepaid_notify
from .refund import handle_refund_notify
from .withdraw import handle_withdraw_notify
from .models import VirtualAccountSystem
from .query_notify import register_query_notify_handle


def init_test_pay_notify_handles():
    from api_x.zyt.evas.test_pay.constant import BizType, NotifyType
    from api_x.zyt.evas.test_pay.notify import register_notify_handle, register_pay_to_bankcard_notify_handle

    # payment
    register_notify_handle(TransactionType.PAYMENT, BizType.PAY, NotifyType.Pay.SYNC, handle_payment_result)
    register_notify_handle(TransactionType.PAYMENT, BizType.PAY, NotifyType.Pay.ASYNC, handle_payment_notify)

    # prepaid
    register_notify_handle(TransactionType.PREPAID, BizType.PAY, NotifyType.Pay.SYNC, handle_prepaid_result)
    register_notify_handle(TransactionType.PREPAID, BizType.PAY, NotifyType.Pay.ASYNC, handle_prepaid_notify)

    # refund
    register_notify_handle(TransactionType.REFUND, BizType.REFUND, NotifyType.Refund.ASYNC, handle_refund_notify)

    # pay_to_bankcard
    register_pay_to_bankcard_notify_handle(TransactionType.WITHDRAW, handle_withdraw_notify)


def init_lianlian_pay_notify_handles():
    from api_x.zyt.evas.lianlian_pay import NAME
    from api_x.zyt.evas.lianlian_pay.constant import NotifyType
    from api_x.zyt.evas.lianlian_pay.notify import register_pay_notify_handle, register_refund_notify_handle
    from api_x.zyt.evas.lianlian_pay.notify import register_pay_to_bankcard_notify_handle
    from api_x.zyt.evas.lianlian_pay import query_refund_notify

    # payment
    register_pay_notify_handle(TransactionType.PAYMENT, NotifyType.Pay.SYNC, handle_payment_result)
    register_pay_notify_handle(TransactionType.PAYMENT, NotifyType.Pay.ASYNC, handle_payment_notify)

    # prepaid
    register_pay_notify_handle(TransactionType.PREPAID, NotifyType.Pay.SYNC, handle_prepaid_result)
    register_pay_notify_handle(TransactionType.PREPAID, NotifyType.Pay.ASYNC, handle_prepaid_notify)

    # refund
    register_refund_notify_handle(TransactionType.REFUND, handle_refund_notify)

    # pay_to_bankcard
    register_pay_to_bankcard_notify_handle(TransactionType.WITHDRAW, handle_withdraw_notify)

    # query_notify
    # notify(source, sn, sn_created_on[, vas_sn])
    register_query_notify_handle(TransactionType.REFUND, NAME, query_refund_notify)


def init_weixin_pay_notify_handles():
    from api_x.zyt.evas.weixin_pay import NAME
    from api_x.zyt.evas.weixin_pay.constant import NotifyType
    from api_x.zyt.evas.weixin_pay.notify import register_pay_notify_handle, register_refund_notify_handle
    from api_x.zyt.evas.weixin_pay import query_pay_notify, query_refund_notify

    # payment
    register_pay_notify_handle(TransactionType.PAYMENT, NotifyType.Pay.SYNC, handle_payment_result)
    register_pay_notify_handle(TransactionType.PAYMENT, NotifyType.Pay.ASYNC, handle_payment_notify)

    # prepaid
    register_pay_notify_handle(TransactionType.PREPAID, NotifyType.Pay.SYNC, handle_prepaid_result)
    register_pay_notify_handle(TransactionType.PREPAID, NotifyType.Pay.ASYNC, handle_prepaid_notify)

    # refund
    register_refund_notify_handle(TransactionType.REFUND, handle_refund_notify)

    # query_notify
    # notify(source, sn, sn_created_on[, vas_sn])
    register_query_notify_handle(TransactionType.PAYMENT, NAME, query_pay_notify)
    register_query_notify_handle(TransactionType.REFUND, NAME, query_refund_notify)


def init_zyt_pay_notify_handles():
    from .payment import handle_paid_out
    from .refund import handle_refund_in
    from api_x.zyt.vas.constant import NotifyType
    from api_x.zyt.vas.notify import register_pay_notify_handle, register_refund_notify_handle

    # payment
    register_pay_notify_handle(TransactionType.PAYMENT, NotifyType.Pay.SYNC, handle_payment_result)
    register_pay_notify_handle(TransactionType.PAYMENT, NotifyType.Pay.ASYNC, handle_payment_notify)
    register_pay_notify_handle(TransactionType.PAYMENT, NotifyType.Pay.PAID_OUT, handle_paid_out)

    # refund
    register_refund_notify_handle(TransactionType.REFUND, NotifyType.Refund.ASYNC, handle_refund_notify)
    register_refund_notify_handle(TransactionType.REFUND, NotifyType.Refund.REFUND_IN, handle_refund_in)


def init_register_notify_handles():
    init_test_pay_notify_handles()
    init_lianlian_pay_notify_handles()
    init_weixin_pay_notify_handles()
    init_zyt_pay_notify_handles()
