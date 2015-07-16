# coding=utf-8
from __future__ import unicode_literals
from tools.dbi import from_db, transactional


def two_accounts_bookkeeping(event, debit_account, credit_account):
    amount = event['amount']
    return debit_credit_bookkeeping(event, ((debit_account, amount),), ((credit_account, amount),))


@transactional
def debit_credit_bookkeeping(event, debit_items, credit_items):
    """ 复式记账法
    :param event: 事件
    :param debit_items: 借记事项[(account, amount), ...]
    :param credit_items: 贷记事项((account, amount), ...)
    :return:
    """
    amount = event['amount']
    debits_amount = sum(a for _, a in debit_items)
    credits_amount = sum(a for _, a in credit_items)
    if not amount == debits_amount == credits_amount:
        raise ValueError('event, debit and credit amount are not equal.')

    created_on = event['created_on']
    account_id = event['account_id']

    db = from_db()
    event_id = db.insert('event', returns_id=True, **event)

    for account, amount in debit_items:
        account_log = {
            'event_id': event_id,
            'account_id': account_id,
            'side': 'debit',  # 借
            'amount': amount,
            'created_on': created_on
        }
        db.insert(account + '_account_transaction_log', **account_log)

    for account, amount in credit_items:
        account_log = {
            'event_id': event_id,
            'account_id': account_id,
            'side': 'credit',  # 贷
            'amount': amount,
            'created_on': created_on
        }
        db.insert(account + '_account_transaction_log', **account_log)
