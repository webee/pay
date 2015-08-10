#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals, print_function
from decimal import Decimal

import sys

from flask.ext.script import Manager, Server
from api import create_app


manager = Manager(create_app)
manager.add_option('-e', '--env', dest='env', required=False)

server = Server(host="0.0.0.0", port=5000)
manager.add_command("runserver", server)


@manager.command
def init_db():
    from ops.deploy.init_db import init_db
    init_db()


def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    manager.run()


@manager.option('-u', '--user_domain', type=long, dest="user_domain_id", required=True)
@manager.option('-i', '--user_id', type=str, dest="user_id", required=True)
def test_create_user(user_domain_id, user_id):
    """新建用户"""
    from api.account._dba import _create_account

    account_id = _create_account(user_domain_id, user_id)

    print('account_id: %r' % account_id)


@manager.option('-i', '--id', type=long, dest="account_id", required=True)
@manager.option('-a', '--amount', type=Decimal, dest="amount", required=True)
def test_prepaid(account_id, amount):
    """充值"""
    from api.core.prepaid import prepaid

    prepaid(account_id, amount)


@manager.option('-i', '--id', type=long, dest="account_id", required=True)
@manager.option('-a', '--amount', type=Decimal, dest="amount", required=True)
@manager.option('-b', '--bankcard', type=int, dest="bankcard_id", required=True)
def test_withdraw(account_id, amount, bankcard_id):
    """申请提现"""
    from api.core.withdraw import _create_withdraw

    withdraw_id = _create_withdraw(account_id, bankcard_id, amount, '')
    print('withdraw_id: %r' % withdraw_id)


@manager.option('-i', '--id', type=str, dest="withdraw_id", required=True)
@manager.option('-s', '--state', type=int, dest="state", required=True)
def test_done_withdraw(withdraw_id, state):
    """完成提现"""
    from api.core.withdraw import _fail_withdraw, _succeed_withdraw

    if state:
        _succeed_withdraw(withdraw_id)
    else:
        _fail_withdraw(withdraw_id)


@manager.option('-f', '--from', type=long, dest="from_id", required=True)
@manager.option('-t', '--to', type=long, dest="to_id", required=True)
@manager.option('-a', '--amount', type=Decimal, dest="amount", required=True)
@manager.option('-i', '--info', type=unicode, dest="info")
def test_transfer(from_id, to_id, amount, info):
    from api.core.transfer import transfer

    info = info or '转账'
    transfer('', info, from_id, to_id, amount)


if __name__ == '__main__':
    main()
