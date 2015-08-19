#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals, print_function
from decimal import Decimal

from flask.ext.script import Manager, Shell, Server
from api_x import create_app


manager = Manager(create_app)
manager.add_option('-e', '--env', dest='env', default='dev', required=False)


def make_shell_context():
    import api_x
    from api_x import config, db
    return dict(api=api_x, app=manager.app, config=config, db=db)


manager.add_command("shell", Shell(make_context=make_shell_context))

server = Server(host="0.0.0.0", port=5000)
manager.add_command("runserver", server)


@manager.option('-r', '--recreate', action="store_true", dest="recreate", required=False, default=False)
def init_db(recreate):
    from fabric.api import local
    from api_x import db
    from api_x.data import init_data

    def recreate_db():
        from tools.log import info
        info('recreating database ...')
        local('mysql -u root -p < migration/init_db.sql')

    if recreate:
        recreate_db()
    db.drop_all()
    db.create_all()
    init_data()


@manager.command
def test_create_user():
    from api_x.zyt.vas.user import create_user

    user = create_user()

    print('user_id: {0}'.format(user.id))


@manager.option('-i', '--id', type=long, dest="user_id", required=True)
def test_get_user_balance(user_id):
    from api_x.zyt.vas.user import get_user_cash_balance

    cash_balance = get_user_cash_balance(user_id)
    print('#{0}: total: {1}, available: {2}, frozen: {3}'.format(user_id,
                                                                 cash_balance.total,
                                                                 cash_balance.available,
                                                                 cash_balance.frozen))


@manager.option('-i', '--id', type=long, dest="user_id", required=True)
@manager.option('-a', '--amount', type=Decimal, dest="amount", required=True)
@manager.option('-f', '--fail', action="store_true", dest="failed", default=False)
def test_prepaid(user_id, amount, failed):
    from api_x.zyt.biz.vas import get_vas_by_name
    from api_x.zyt.biz import prepaid

    vas = get_vas_by_name('test_pay')
    prepaid_record = prepaid.create_prepaid(user_id, amount, vas.name, '测试充值')

    if failed:
        # es test pay failed notify.
        prepaid.fail_prepaid(prepaid_record)
    else:
        # es test pay success notify.
        prepaid.succeed_prepaid(vas.id, prepaid_record)



@manager.option('-i', '--id', type=long, dest="user_id", required=True)
@manager.option('-a', '--amount', type=Decimal, dest="amount", required=True)
@manager.option('-b', '--bankcard', type=int, dest="bankcard_id", required=True)
def test_withdraw(user_id, amount, bankcard_id):
    pass


@manager.option('-i', '--id', type=long, dest="withdraw_id", required=True)
@manager.option('-s', '--success', type=int, dest="success", default=1)
def test_done_withdraw(withdraw_id, success):
    from api_x.zyt.biz.vas import get_vas_by_name
    from api_x.dbs import require_transaction_context
    from datetime import datetime
    from api_x.zyt.biz import withdraw

    es = get_vas_by_name('test_pay')
    if success:
        with require_transaction_context():
            withdraw_record = withdraw.update_withdraw_info(withdraw_id,
                                                            't:{0}'.format(datetime.now().strftime('%f')),
                                                            'SUCCESS', 'SUCCESS')
            withdraw.succeed_withdraw(es.id, withdraw_record)
    else:
        with require_transaction_context():
            withdraw_record = withdraw.update_withdraw_info(withdraw_id,
                                                            't:{0}'.format(datetime.now().strftime('%f')),
                                                            'FAILED', 'FAILED')
            withdraw.fail_withdraw(withdraw_record)


@manager.option('-f', '--from', type=long, dest="from_id", required=True)
@manager.option('-t', '--to', type=long, dest="to_id", required=True)
@manager.option('-a', '--amount', type=Decimal, dest="amount", required=True)
def test_transfer(from_id, to_id, amount):
    from api_x import zyt
    from api_x.zyt.biz.vas import get_vas_by_name
    from api_x.zyt.biz import transfer

    zyt = get_vas_by_name(zyt.NAME)
    transfer.create_transfer(from_id, to_id, amount, zyt.name, '测试转账')


if __name__ == '__main__':
    manager.run()
