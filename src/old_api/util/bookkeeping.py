# coding=utf-8
from __future__ import unicode_literals
from datetime import datetime

from pytoolbox.util.dbe import db_context

ACCOUNTS_SIDES = {
    'asset': {'+': 'd', '-': 'c'},
    'secured': {'-': 'd', '+': 'c'},
    'business': {'-': 'd', '+': 'c'},
    'frozen': {'-': 'd', '+': 'c'},
    'cash': {'-': 'd', '+': 'c'},
}


class Event(object):
    def __init__(self, account_id, source_type, step, source_id, amount):
        self.account_id = account_id
        self.source_type = source_type
        self.step = step
        self.source_id = source_id
        self.amount = amount
        self.created_on = datetime.now()


def get_account_side_sign(account):
    sides = ACCOUNTS_SIDES[account]
    positive_side, negative_side = sides['+'], sides['-']
    if positive_side == 'd' and negative_side == 'c':
        return 1, -1
    elif negative_side == 'd' and positive_side == 'c':
        return -1, 1
    raise ValueError('impossible!')


def bookkeeping(event, account_a, account_b):
    sa, account_a = account_a[0], account_a[1:]
    sb, account_b = account_b[0], account_b[1:]
    if sa == '+' and sb == '-':
        debit_account, credit_account = _get_debit_and_credit(account_a, account_b)
    elif sa == '-' and sb == '+':
        debit_account, credit_account = _get_debit_and_credit(account_b, account_a)
    elif sa == '+' and sb == '+':
        debit_account, credit_account = _get_debit_and_credit_both_increased(account_b, account_a)
    elif sa == '-' and sb == '-':
        debit_account, credit_account = _get_debit_and_credit_both_decreased(account_b, account_a)
    else:
        raise ValueError('bad accounts format.')
    amount = event.amount
    return _debit_credit_bookkeeping(event, ((debit_account, amount),), ((credit_account, amount),))


def _get_debit_and_credit_both_increased(account_a, account_b):
    """ 都增加
    """
    debit_accounts, credit_accounts = _get_debit_and_credit_accounts((account_a, account_b), ())

    return debit_accounts[0], credit_accounts[0]


def _get_debit_and_credit_both_decreased(account_a, account_b):
    """ 都减少
    """
    debit_accounts, credit_accounts = _get_debit_and_credit_accounts((), (account_a, account_b))

    return debit_accounts[0], credit_accounts[0]


def _get_debit_and_credit(increased_account, decreased_account):
    """ 一增一减
    """
    debit_accounts, credit_accounts = _get_debit_and_credit_accounts((increased_account, ), (decreased_account, ))

    return debit_accounts[0], credit_accounts[0]


def _get_debit_and_credit_accounts(increased_accounts, decreased_accounts):
    accounts = {account: ACCOUNTS_SIDES[account]['+'] for account in increased_accounts}
    accounts.update({account: ACCOUNTS_SIDES[account]['-'] for account in decreased_accounts})

    debit_accounts = [account for account, s in accounts.items() if s == 'd']
    credit_accounts = [account for account, s in accounts.items() if s == 'c']

    return debit_accounts, credit_accounts


def _debit_credit_bookkeeping(event, debit_items, credit_items):
    """ 复式记账法
    :param event: 事件
    :param debit_items: 借记事项[(account, amount), ...]
    :param credit_items: 贷记事项((account, amount), ...)
    :return:
    """
    if not _is_balanced(event.amount, debit_items, credit_items):
        raise ValueError('event, debit and credit amount are not equal.')

    created_on = event.created_on
    account_id = event.account_id

    event_id = _create_event(event)
    _record_debit(event_id, account_id, debit_items, created_on)
    _record_credit(event_id, account_id, credit_items, created_on)
    return True


def _is_balanced(event_amount, debit_items, credit_items):
    debits_amount = sum(a for _, a in debit_items)
    credits_amount = sum(a for _, a in credit_items)
    return event_amount == debits_amount == credits_amount


@db_context
def _create_event(db, event):
    return db.insert('event', returns_id=True, **event.__dict__)


@db_context
def _record_debit(db, event_id, account_id, debit_items, created_on):
    for account, amount in debit_items:
        account_log = {
            'event_id': event_id,
            'account_id': account_id,
            'side': 'debit',
            'amount': amount,
            'created_on': created_on
        }
        db.insert(account + '_account_transaction_log', **account_log)


@db_context
def _record_credit(db, event_id, account_id, credit_items, created_on):
    for account, amount in credit_items:
        account_log = {
            'event_id': event_id,
            'account_id': account_id,
            'side': 'credit',
            'amount': amount,
            'created_on': created_on
        }
        db.insert(account + '_account_transaction_log', **account_log)
