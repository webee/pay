# coding=utf-8
from __future__ import unicode_literals
from tools.dbi import transactional


def two_accounts_bookkeeping(account_id, source_type, source_id, amount, debit_account, credit_account):
    return bookkeeping(account_id, source_type, source_id, ((debit_account, amount),), ((credit_account, amount),))


@transactional
def bookkeeping(account_id, source_type, source_id, debit_items, credit_items):
    """ 复式记账法
    :param account_id: 记账用户
    :param source_type: 事件来源类型
    :param source_id: 事件来源id
    :param debit_items: 借记事项[(account, amount), ...]
    :param credit_items: 贷记事项((account, amount), ...)
    :return:
    """
    debits_amount = sum(a for _, a in debit_items)
    credits_amount = sum(a for _, a in credit_items)
    if debits_amount != credits_amount:
        raise ValueError('debit and credit amount not equal.')

    amount = debits_amount

    now = datetime.now()
    event = {
        'account_id': account_id,
        'source_type': source_type,
        'source_id': source_id,
        'amount': amount,
        'created_on': now
    }

    db = from_db()
    event_id = db.insert('event', returns_id=True, **event)

    for account, amount in debit_items:
        account_log = {
            'event_id': event_id,
            'account_id': account_id,
            'side': 'debit',  # 借
            'amount': amount,
            'created_on': now
        }
        db.insert(account + '_account_transaction_log', **account_log)

    for account, amount in credit_items:
        account_log = {
            'event_id': event_id,
            'account_id': account_id,
            'side': 'credit',  # 贷
            'amount': amount,
            'created_on': now
        }
        db.insert(account + '_account_transaction_log', **account_log)
