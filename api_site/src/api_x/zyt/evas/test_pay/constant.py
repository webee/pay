# coding=utf-8


class BizType:
    PAY = 'PAY'
    REFUND = 'REFUND'
    PAY_TO_BANK = 'PAY_TO_BANK'


class NotifyType:
    class Pay:
        SYNC = 'SYNC'
        ASYNC = 'ASYNC'

    class Refund:
        ASYNC = 'ASYNC'
