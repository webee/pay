# coding=utf-8
from api.constant import SourceType, RefundStep
from api.util.bookkeeping import bookkeeping, Event


def frozen(account_id, source_id, amount):
    return bookkeeping(Event(account_id, SourceType.REFUND, RefundStep.FROZEN, source_id, amount),
                       '-secured', '+frozen')


def unfrozen_back(account_id, source_id, amount):
    return bookkeeping(Event(account_id, SourceType.REFUND, RefundStep.FAILED, source_id, amount),
                       '-frozen', '+secured')


def unfrozen_out(account_id, source_id, amount):
    return bookkeeping(Event(account_id, SourceType.REFUND, RefundStep.SUCCESS, source_id, amount),
                       '-frozen', '-asset')