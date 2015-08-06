#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals, print_function
from decimal import Decimal

from flask.ext.script import Manager, Shell, Server
import requests

from api import create_app

manager = Manager(create_app)
manager.add_option('-e', '--env', dest='env', required=False)


def make_shell_context():
    return dict(app=manager.app)


manager.add_command("shell", Shell(make_context=make_shell_context))

server = Server(host="0.0.0.0", port=5000)
manager.add_command("runserver", server)


@manager.command
def init_db():
    from ops.deploy.init_db import init_db
    init_db()


####################
# for test command.
####################


@manager.option('-i', '--id', type=long, dest="account_id", required=True)
@manager.option('-a', '--amount', type=Decimal, dest="amount", required=True)
def test_prepaid(account_id, amount):
    """ 充值
    :param account_id:
    :param amount:
    :return:
    """
    from pytoolbox.util.dbe import require_transaction_context
    from api.constant import SourceType, PrepaidStep
    from api.util.bookkeeping import Event, bookkeeping

    with require_transaction_context():
        bookkeeping(Event(account_id, SourceType.PREPAID, PrepaidStep.SUCCESS, "", amount),
                    '+asset', '+cash')


@manager.option('-i', '--id', type=long, dest="account_id", required=True)
@manager.option('-a', '--amount', type=Decimal, dest="amount", required=True)
def test_withdraw(account_id, amount):
    """ 直接提现
    :param account_id:
    :param amount:
    :return:
    """
    from pytoolbox.util.dbe import require_transaction_context
    from api.constant import SourceType, PrepaidStep
    from api.util.bookkeeping import Event, bookkeeping
    from api.account.withdraw import require_lock_user_account
    from api.account.account import get_cash_balance
    from api.account.error import InsufficientBalanceError

    with require_lock_user_account(account_id, 'cash'):
        with require_transaction_context():
            balance = get_cash_balance(account_id)
            if amount > balance:
                raise InsufficientBalanceError()
            bookkeeping(Event(account_id, SourceType.WITHDRAW, PrepaidStep.SUCCESS, "", amount),
                        '-cash', '-asset')


@manager.option('-f', '--from', type=long, dest="from_id", required=True)
@manager.option('-t', '--to', type=long, dest="to_id", required=True)
@manager.option('-a', '--amount', type=Decimal, dest="amount", required=True)
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

    from pytoolbox.util.dbe import require_transaction_context
    from tools.lock import require_user_account_lock, GetLockTimeoutError, GetLockError
    from api.account import account
    from api.constant import SourceType, TransferStep
    from api.util.bookkeeping import Event, bookkeeping

    if amount <= Decimal('0'):
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
def test_settle_user_cash_balance(account_id):
    from api.account.account.balance import settle_user_account_balance

    settle_user_account_balance(account_id, 'cash')


if __name__ == '__main__':
    manager.run()
