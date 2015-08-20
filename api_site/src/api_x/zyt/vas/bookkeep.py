# coding=utf-8
from __future__ import unicode_literals
from datetime import datetime

from api_x import db
from api_x.zyt.vas.models import Event, SystemAssetAccountItem, UserLiabilityAccountItem, LiabilityType, EventType
from api_x.zyt.vas.models import UserCashBalanceLog, UserCashBalance
from api_x.zyt.vas.user import get_account_user
from .error import InsufficientAvailableBalanceError, InsufficientFrozenBalanceError, AmountValueError, \
    AccountUserLockedError
from pytoolbox.util.dbs import transactional


DEBIT = 'DEBIT'
CREDIT = 'CREDIT'

_event_actions = {}


def _register_event_action(event_type):
    def register(func):
        _event_actions[event_type] = func
        return func
    return register


@transactional
def bookkeeping(event_type, transaction_sn, user_id, vas_name, amount):
    if amount <= 0:
        raise AmountValueError()

    account_user = get_account_user(user_id)
    if account_user.is_locked:
        raise AccountUserLockedError(user_id)

    event = _create_event(transaction_sn, user_id, vas_name, event_type, amount)
    _event_actions[event_type](event)
    _update_balance(event)

    return event.id


@_register_event_action(EventType.TRANSFER_IN)
def _transfer_in(event):
    """转入记账: +asset, +liability:[available,total]"""
    user_id, vas_name, amount = event.user_id, event.vas_name, event.amount

    _bkkp_asset(user_id, vas_name, event, DEBIT, amount)
    _bkkp_liability(user_id, event, LiabilityType.AVAILABLE, CREDIT, amount)
    _bkkp_liability(user_id, event, LiabilityType.TOTAL, CREDIT, amount)


@_register_event_action(EventType.TRANSFER_OUT)
def _transfer_out(event):
    """转出记账: -asset, -liability:[available,total]"""
    user_id, vas_name, amount = event.user_id, event.vas_name, event.amount

    _bkkp_asset(user_id, vas_name, event, CREDIT, amount)
    _bkkp_liability(user_id, event, LiabilityType.AVAILABLE, DEBIT, amount)
    _bkkp_liability(user_id, event, LiabilityType.TOTAL, DEBIT, amount)


@_register_event_action(EventType.FREEZE)
def _freeze_cash(event):
    """冻结记账: -liability:available, +liability:frozen"""
    user_id, vas_name, amount = event.user_id, event.vas_name, event.amount

    _bkkp_liability(user_id, event, LiabilityType.AVAILABLE, DEBIT, amount)
    _bkkp_liability(user_id, event, LiabilityType.FROZEN, CREDIT, amount)


@_register_event_action(EventType.UNFREEZE)
def _unfreeze_cash(event):
    """解冻记账: -liability:frozen, +liability:available"""
    user_id, vas_name, amount = event.user_id, event.vas_name, event.amount

    _bkkp_liability(user_id, event, LiabilityType.AVAILABLE, CREDIT, amount)
    _bkkp_liability(user_id, event, LiabilityType.FROZEN, DEBIT, amount)


@_register_event_action(EventType.TRANSFER_IN_FROZEN)
def _transfer_in_frozen(event):
    """转入冻结记账: +asset, +liability:[frozen,total]"""
    user_id, vas_name, amount = event.user_id, event.vas_name, event.amount

    _bkkp_asset(user_id, vas_name, event, DEBIT, amount)
    _bkkp_liability(user_id, event, LiabilityType.FROZEN, CREDIT, amount)
    _bkkp_liability(user_id, event, LiabilityType.TOTAL, CREDIT, amount)


@_register_event_action(EventType.TRANSFER_OUT_FROZEN)
def _transfer_out_frozen(event):
    """转出冻结记账: -asset, -liability:[frozen,total]"""
    user_id, vas_name, amount = event.user_id, event.vas_name, event.amount

    _bkkp_asset(user_id, vas_name, event, CREDIT, amount)
    _bkkp_liability(user_id, event, LiabilityType.FROZEN, DEBIT, amount)
    _bkkp_liability(user_id, event, LiabilityType.TOTAL, DEBIT, amount)


def _create_event(transaction_sn, user_id, vas_name, event_type, amount):
    now = datetime.utcnow()
    event = Event(transaction_sn=transaction_sn, user_id=user_id, vas_name=vas_name,
                  type=event_type, amount=amount, created_on=now)
    db.session.add(event)
    db.session.flush()

    return event


def _bkkp_asset(user_id, vas_name, event, side, amount):
    account_item = SystemAssetAccountItem(user_id=user_id, vas_name=vas_name, event_id=event.id,
                                          side=side, amount=amount, created_on=event.created_on)
    db.session.add(account_item)


def _bkkp_liability(user_id, event, l_type, side, amount):
    account_item = UserLiabilityAccountItem(user_id=user_id, event_id=event.id, type=l_type,
                                            side=side, amount=amount, created_on=event.created_on)
    db.session.add(account_item)


def _update_balance(event):
    event_type, user_id, amount = event.type, event.user_id, event.amount

    cash_balance = UserCashBalance.query.filter_by(user_id=user_id).one()

    if event_type == EventType.TRANSFER_IN:
        cash_balance.available = UserCashBalance.available + amount
        cash_balance.total = UserCashBalance.total + amount
    elif event_type == EventType.FREEZE:
        cash_balance.available = UserCashBalance.available - amount
        cash_balance.frozen = UserCashBalance.frozen + amount
    elif event_type == EventType.UNFREEZE:
        cash_balance.available = UserCashBalance.available + amount
        cash_balance.frozen = UserCashBalance.frozen - amount
    elif event_type == EventType.TRANSFER_OUT:
        cash_balance.available = UserCashBalance.available - amount
        cash_balance.total = UserCashBalance.total - amount
    elif event_type == EventType.TRANSFER_IN_FROZEN:
        cash_balance.frozen = UserCashBalance.frozen + amount
        cash_balance.total = UserCashBalance.total + amount
    elif event_type == EventType.TRANSFER_OUT_FROZEN:
        cash_balance.frozen = UserCashBalance.frozen - amount
        cash_balance.total = UserCashBalance.total - amount

    db.session.add(cash_balance)
    cash_balance = UserCashBalance.query.filter_by(user_id=user_id).one()
    if cash_balance.available < 0 or cash_balance.frozen < 0:
        raise InsufficientAvailableBalanceError()
    if cash_balance.frozen < 0:
        raise InsufficientFrozenBalanceError()

    cash_balance_log = UserCashBalanceLog(user_id=user_id, event=event,
                                          total=cash_balance.total,
                                          available=cash_balance.available,
                                          frozen=cash_balance.frozen)
    db.session.add(cash_balance_log)
