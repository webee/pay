# -*- coding: utf-8 -*-
from datetime import datetime

from pytoolbox.util.dbe import db_context


class SourceType(object):
    PAY = 'PAY'
    WITHDRAW_FROZEN = 'WITHDRAW:FROZEN'
    WITHDRAW_SUCCESS = 'WITHDRAW:SUCCESS'
    WITHDRAW_FAILED = 'WITHDRAW:FAILED'
    REFUND = 'REFUND'
    TRANSFER = 'TRANSFER'


class Event(object):
    def __init__(self, source_type, source_id, amount):
        self.source_type = source_type
        self.source_id = source_id
        self.amount = amount
        self.created_on = datetime.now()


@db_context
def bookkeep(db, event, credit_account, debit_account):
    credit_account_id, credit_account_name = credit_account
    debit_account_id, debit_account_name = debit_account

    event_id = _create_event(db, event)
    _credit(event_id, credit_account_id, credit_account_name, event.amount, event.created_on) # -
    _debit(event_id, debit_account_id, debit_account_name, event.amount, event.created_on) # +


@db_context
def cash_debit(db, event, debit_account_id):
    event_id = _create_event(db, event)
    _debit(event_id, debit_account_id, 'cash', event.amount, event.created_on) # +


@db_context
def cash_credit(db, event, credit_account_id):
    event_id = _create_event(db, event)
    _credit(event_id, credit_account_id, 'cash', event.amount, event.created_on) # -


@db_context
def _create_event(db, event):
    return db.insert('event', returns_id=True, **event.__dict__)


@db_context
def _debit(db, event_id, account_id, account_name, amount, created_on):
    _record_transaction(db, account_name, event_id, account_id, 'debit', amount, created_on)


@db_context
def _credit(db, event_id, account_id, account_name, amount, created_on):
    _record_transaction(db, account_name, event_id, account_id, 'credit', amount, created_on)


@db_context
def _record_transaction(db, account_name, event_id, account_id, direction, amount, created_on):
    account_log = {
        'event_id': event_id,
        'account_id': account_id,
        'side': direction,
        'amount': amount,
        'created_on': created_on
    }
    db.insert('{0}_account_transaction_log'.format(account_name), **account_log)
