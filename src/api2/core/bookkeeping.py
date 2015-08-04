# -*- coding: utf-8 -*-
from datetime import datetime

from pytoolbox.util.dbe import db_context


class SourceType(object):
    PAY = 'PAY'
    WITHDRAW = 'WITHDRAW'
    REFUND = 'REFUND'
    TRANSFER = 'TRANSFER'


class Event(object):
    def __init__(self, source_type, source_id, amount):
        self.source_type = source_type
        self.source_id = source_id
        self.amount = amount
        self.created_on = datetime.now()


@db_context
def bookkeep(db, event, credit_account_id, debit_account_id):
    event_id = _create_event(db, event)
    _record_credit(event_id, credit_account_id, event.amount, event.created_on)
    _record_debit(event_id, debit_account_id, event.amount, event.created_on)


@db_context
def _create_event(db, event):
    return db.insert('event', returns_id=True, **event.__dict__)


@db_context
def _record_debit(db, event_id, account_id, amount, created_on):
    _record_transaction(db, event_id, account_id, 'debit', amount, created_on)


@db_context
def _record_credit(db, event_id, account_id, amount, created_on):
    _record_transaction(db, event_id, account_id, 'credit', amount, created_on)


@db_context
def _record_transaction(db, event_id, account_id, direction, amount, created_on):
    account_log = {
        'event_id': event_id,
        'account_id': account_id,
        'side': direction,
        'amount': amount,
        'created_on': created_on
    }
    db.insert('transaction_log_between_accounts', **account_log)
