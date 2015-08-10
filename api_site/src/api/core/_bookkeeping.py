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
    PREPAID = 'PREPAID'

SOURCE_TYPE_TABLE_MAP = {SourceType.PAY: 'payment',
                         SourceType.WITHDRAW_FROZEN: 'withdraw',
                         SourceType.WITHDRAW_SUCCESS: 'withdraw',
                         SourceType.WITHDRAW_FAILED: 'withdraw',
                         SourceType.REFUND: 'refund',
                         SourceType.TRANSFER: 'transfer',
                         SourceType.PREPAID: 'prepaid',
                         }


_ACCOUNTS_SIDES = {
    'asset': {'+': 'd', '-': 'c'},
    'frozen': {'-': 'd', '+': 'c'},
    'cash': {'-': 'd', '+': 'c'},
}


class Event(object):
    def __init__(self, source_type, source_id, amount, trade_info):
        self.source_type = source_type
        self.source_id = source_id
        self.amount = amount
        self.trade_info = trade_info
        self.created_on = datetime.now()


@db_context
def bookkeep(db, event, account_a, account_b):
    account_id_a, account_name_a = account_a
    account_id_b, account_name_b = account_b

    sa, account_name_a = account_name_a[0], account_name_a[1:]
    sb, account_name_b = account_name_b[0], account_name_b[1:]
    # account_id_map = {
    #     account_name_a: account_id_a,
    #     account_name_b: account_id_b,
    # }

    if sa == '+' and sb == '-':
        debit_account, debit_account_id, credit_account, credit_account_id = \
            _get_debit_and_credit(account_name_a, account_id_a, account_name_b, account_id_b)
    elif sa == '-' and sb == '+':
        debit_account, debit_account_id, credit_account, credit_account_id = \
            _get_debit_and_credit(account_name_b, account_id_b, account_name_a, account_id_a)
    elif sa == '+' and sb == '+':
        debit_account, debit_account_id, credit_account, credit_account_id = \
            _get_debit_and_credit_both_increased(account_name_a, account_id_a, account_name_b, account_id_b)
    elif sa == '-' and sb == '-':
        debit_account, debit_account_id, credit_account, credit_account_id = \
            _get_debit_and_credit_both_decreased(account_name_a, account_id_a, account_name_b, account_id_b)
    else:
        raise ValueError('bad accounts format.')

    event_id = _create_event(db, event)
    _credit(event_id, credit_account_id, credit_account, event.amount, event.created_on)
    _debit(event_id, debit_account_id, debit_account, event.amount, event.created_on)


@db_context
def transfer_bookkeep(db, event, from_id, to_id):
    event_id = _create_event(db, event)
    _credit(event_id, to_id, 'cash', event.amount, event.created_on)
    _debit(event_id, from_id, 'cash', event.amount, event.created_on)


def get_account_side_sign(account):
    sides = _ACCOUNTS_SIDES[account]
    positive_side, negative_side = sides['+'], sides['-']
    if positive_side == 'd' and negative_side == 'c':
        return 1, -1
    elif negative_side == 'd' and positive_side == 'c':
        return -1, 1
    raise ValueError('impossible!')


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


def _get_debit_and_credit_both_increased(account_a, account_a_id, account_b, account_b_id):
    """ 都增加
    """
    debit_accounts, credit_accounts = _get_debit_and_credit_accounts([(account_a, account_a_id),
                                                                      (account_b, account_b_id)], ())
    return debit_accounts[0][0], debit_accounts[0][1], credit_accounts[0][0], credit_accounts[0][1]


def _get_debit_and_credit_both_decreased(account_a, account_a_id, account_b, account_b_id):
    """ 都减少
    """
    debit_accounts, credit_accounts = _get_debit_and_credit_accounts((), [(account_a, account_a_id),
                                                                          (account_b, account_b_id)])
    return debit_accounts[0][0], debit_accounts[0][1], credit_accounts[0][0], credit_accounts[0][1]


def _get_debit_and_credit(increased_account, increased_account_id, decreased_account, decreased_account_id):
    """ 一增一减
    """
    debit_accounts, credit_accounts = _get_debit_and_credit_accounts([(increased_account, increased_account_id)],
                                                                     [(decreased_account, decreased_account_id)])
    return debit_accounts[0][0], debit_accounts[0][1], credit_accounts[0][0], credit_accounts[0][1]


def _get_debit_and_credit_accounts(increased_accounts, decreased_accounts):
    accounts = [(account, _ACCOUNTS_SIDES[account]['+'], account_id) for account, account_id in increased_accounts]
    accounts.extend([(account, _ACCOUNTS_SIDES[account]['-'], account_id) for account, account_id in decreased_accounts])

    debit_accounts = [(account, id) for account, s, id in accounts if s == 'd']
    credit_accounts = [(account, id) for account, s, id in accounts if s == 'c']

    return debit_accounts, credit_accounts
