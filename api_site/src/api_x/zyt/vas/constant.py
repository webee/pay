# coding=utf-8
from __future__ import unicode_literals


class BizType:
    PAY = 'PAY'
    REFUND = 'REFUND'


class NotifyType:
    class Pay:
        PAID_OUT = 'PAID_OUT'
        SYNC = 'SYNC'
        ASYNC = 'ASYNC'

    class Refund:
        REFUND_IN = 'REFUND_OUT'
        ASYNC = 'ASYNC'
