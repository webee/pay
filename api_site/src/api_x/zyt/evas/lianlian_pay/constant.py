# coding=utf-8


class BizType:
    PAY = 'PAY'
    REFUND = 'REFUND'
    PAY_TO_BANK = 'PAY_TO_BANK'
    QUERY_BIN = 'QUERY_BIN'


class NotifyType:
    class Pay:
        SYNC = 'SYNC'
        ASYNC = 'ASYNC'

    class Refund:
        ASYNC = 'ASYNC'
