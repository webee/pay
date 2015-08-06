# coding=utf-8
from old_api.constant import WithdrawState
from . import dba
from . import event


def withdraw_frozen(withdraw_id):
    if dba.transit_state(withdraw_id, WithdrawState.FROZEN, WithdrawState.FROZEN):
        withdraw_order = dba.get_withdraw(withdraw_id)
        return event.frozen(withdraw_order.account_id, withdraw_order.id, withdraw_order.amount)


def withdraw_failed(withdraw_id):
    if dba.transit_state(withdraw_id, WithdrawState.FROZEN, WithdrawState.FAILED):
        withdraw_order = dba.get_withdraw(withdraw_id)
        return event.unfrozen_back(withdraw_order.account_id, withdraw_order.id, withdraw_order.amount)


def withdraw_success(withdraw_id):
    if dba.transit_state(withdraw_id, WithdrawState.FROZEN, WithdrawState.SUCCESS):
        withdraw_order = dba.get_withdraw(withdraw_id)
        return event.unfrozen_out(withdraw_order.account_id, withdraw_order.id, withdraw_order.amount)
