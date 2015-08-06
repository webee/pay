# coding=utf-8
from api.constant import SourceType, WithdrawStep
from api.util.bookkeeping import Event, bookkeeping


def frozen(account_id, source_id, amount):
    return bookkeeping(Event(account_id, SourceType.WITHDRAW, WithdrawStep.FROZEN, source_id, amount),
                       '+frozen', '-cash')


def unfrozen_back(account_id, source_id, amount):
    return bookkeeping(Event(account_id, SourceType.WITHDRAW, WithdrawStep.FAILED, source_id, amount),
                       '-frozen', '+cash')


def unfrozen_out(account_id, source_id, amount):
    return bookkeeping(Event(account_id, SourceType.WITHDRAW, WithdrawStep.SUCCESS, source_id, amount),
                       '-frozen', '-asset')
