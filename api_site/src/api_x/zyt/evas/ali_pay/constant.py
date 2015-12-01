# coding=utf-8


class BizType:
    PAY = 'PAY'
    REFUND = 'REFUND'


class NotifyType:
    class Pay:
        SYNC = 'SYNC'
        ASYNC = 'ASYNC'

    class Refund:
        ASYNC = 'ASYNC'
