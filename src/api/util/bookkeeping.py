# coding=utf-8
from __future__ import unicode_literals
from datetime import datetime

from tools.dbi import from_db

ACCOUNTS_SIDES = {
    'asset': {'+': 'd', '-': 'c'},
    'secured': {'-': 'd', '+': 'c'},
    'business': {'-': 'd', '+': 'c'},
    'frozen': {'-': 'd', '+': 'c'},
    'cash': {'-': 'd', '+': 'c'},
}


class Event(object):
    def __init__(self, account_id, source_type, step, source_id, amount):
        self.__account_id = account_id,
        self.__source_type = source_type,
        self.__step = step,
        self.__source_id = source_id,
        self.__amount = amount,
        self.__created_on = datetime.now()

    @property
    def account_id(self):
        return self.__account_id

    @property
    def source_type(self):
        return self.__source_type

    @property
    def step(self):
        return self.__step

    @property
    def source_id(self):
        return self.__source_id

    @property
    def amount(self):
        return self.__amount

    @property
    def created_on(self):
        return self.__created_on

    @property
    def items(self):
        return {'account_id':self.account_id, 'source_type':self.source_type, 'step':self.step,
                'source_id':self.source_id, 'amount':self.amount, 'created_on':self.created_on}


def get_debit_and_credit_both_increased(account_a, account_b):
    """ 都减少
    """
    debit_accounts, credit_accounts = get_debit_and_credit_accounts((account_a, account_b), ())

    return debit_accounts[0], credit_accounts[0]


def get_debit_and_credit_both_decreased(account_a, account_b):
    """ 都增加
    """
    debit_accounts, credit_accounts = get_debit_and_credit_accounts((), (account_a, account_b))

    return debit_accounts[0], credit_accounts[0]


def get_debit_and_credit(increased_account, decreased_account):
    """ 一增一减
    """
    debit_accounts, credit_accounts = get_debit_and_credit_accounts((increased_account, ), (decreased_account, ))

    return debit_accounts[0], credit_accounts[0]


def get_debit_and_credit_accounts(increased_accounts, decreased_accounts):
    accounts = {account: ACCOUNTS_SIDES[account]['+'] for account in increased_accounts}
    accounts.update({account: ACCOUNTS_SIDES[account]['-'] for account in decreased_accounts})

    debit_accounts = [account for account, s in accounts.items() if s == 'd']
    credit_accounts = [account for account, s in accounts.items() if s == 'c']

    return debit_accounts, credit_accounts


def two_accounts_bookkeeping(event, debit_account, credit_account):
    amount = event.amount
    return _debit_credit_bookkeeping(event, ((debit_account, amount),), ((credit_account, amount),))


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


def _is_balanced(event_amount, debit_items, credit_items):
    debits_amount = sum(a for _, a in debit_items)
    credits_amount = sum(a for _, a in credit_items)
    return event_amount == debits_amount == credits_amount


def _create_event(event):
    return from_db().insert('event', returns_id=True, **event.items)


def _record_debit(event_id, account_id, debit_items, created_on):
    for account, amount in debit_items:
        account_log = {
            'event_id': event_id,
            'account_id': account_id,
            'side': 'debit',
            'amount': amount,
            'created_on': created_on
        }
        from_db().insert(account + '_account_transaction_log', **account_log)


def _record_credit(event_id, account_id, credit_items, created_on):
    for account, amount in credit_items:
        account_log = {
            'event_id': event_id,
            'account_id': account_id,
            'side': 'credit',
            'amount': amount,
            'created_on': created_on
        }
        from_db().insert(account + '_account_transaction_log', **account_log)
