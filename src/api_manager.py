#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals, print_function

import os

from flask.ext.script import Manager, Shell, Server
from api import create_app
import requests

app = create_app(os.getenv('SYSTEM_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app)


manager.add_command("shell", Shell(make_context=make_shell_context))

server = Server(host="0.0.0.0", port=5000)
manager.add_command("runserver", server)


@manager.command
def init_db():
    from ops.deploy.init_db import init_db
    init_db()


@manager.command
def confirm_to_pay_all():
    resp = requests.post('http://localhost:5000/pay/auto-confirm')
    if resp.status_code == 200:
        print('Auto pay confirmation completed.')
    else:
        print('Auto pay confirmation failed...')


####################
# for test command.
####################


@manager.option('-i', '--id', type=long, dest="account_id", required=True)
@manager.option('-a', '--amount', type=float, dest="amount", required=True)
def test_prepaid(account_id, amount):
    from tools.dbe import require_transaction_context
    from api.constant import SourceType, PrepaidStep
    from api.util.bookkeeping import Event, bookkeeping

    with require_transaction_context():
        bookkeeping(Event(account_id, SourceType.PREPAID, PrepaidStep.SUCCESS, "", amount),
                    '+asset', '+cash')


@manager.option('-f', '--from', type=long, dest="from_id", required=True)
@manager.option('-t', '--to', type=long, dest="to_id", required=True)
@manager.option('-a', '--amount', type=float, dest="amount", required=True)
def test_transfer(from_id, to_id, amount):
    class AmountNotPositiveError(Exception):
        def __init__(self, amount):
            message = "amount must be positive: [{0}]".format(amount)
            super(AmountNotPositiveError, self).__init__(message)

    class InsufficientBalanceError(Exception):
        def __init__(self):
            message = "insufficient balance error."
            super(InsufficientBalanceError, self).__init__(message)

    class TransferError(Exception):
        def __init__(self):
            message = "transfer error."
            super(TransferError, self).__init__(message)

    from tools.dbe import require_transaction_context
    from tools.lock import require_user_account_lock, GetLockTimeoutError, GetLockError
    from api.account import account
    from api.constant import SourceType, TransferStep
    from api.util.bookkeeping import Event, bookkeeping

    if amount <= 0:
        raise AmountNotPositiveError(amount)

    try:
        with require_user_account_lock(from_id, 'cash') as _:
            balance = account.get_cash_balance(from_id)
            if amount > balance:
                raise InsufficientBalanceError()
            with require_transaction_context():
                bookkeeping(Event(from_id, SourceType.TRANSFER, TransferStep.FROZEN, "", amount),
                            '-cash', '+frozen')

                bookkeeping(Event(to_id, SourceType.TRANSFER, TransferStep.SUCCESS, "", amount),
                            '-frozen', '+cash')
    except GetLockTimeoutError:
        raise TransferError()
    except GetLockError:
        raise TransferError()


@manager.option('-i', '--id', type=long, dest="account_id", required=True)
def test_update_user_cash_balance(account_id):
    from api.task.balance import settle_user_account_balance

    settle_user_account_balance(account_id, 'cash')


if __name__ == '__main__':
    manager.run()
