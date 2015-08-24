#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals, print_function
from decimal import Decimal

from flask.ext.script import Manager, Shell, Server, Command
from api_x import create_app


manager = Manager(create_app)
manager.add_option('-e', '--env', dest='env', default='dev', required=False)


def make_shell_context():
    import api_x
    from api_x import config, db

    return dict(api=api_x, app=manager.app, config=config, db=db)


manager.add_command("shell", Shell(make_context=make_shell_context))

server = Server(host="0.0.0.0", port=5100)
manager.add_command("runserver", server)


@manager.option('-r', '--recreate', action="store_true", dest="recreate", required=False, default=False)
def init_db(recreate):
    from fabric.api import local
    from api_x import db
    from api_x.data import init_data
    from api_x.zyt.user_mapping import init_api_entries

    def recreate_db():
        from tools.console_log import info

        info('recreating database ...')
        local('mysql -u root -p < migration/init_db.sql')

    if recreate:
        recreate_db()
    db.drop_all()
    db.create_all()
    init_data()

    init_api_entries()

@manager.command
def update_api_entries():
    from api_x.zyt.user_mapping import init_api_entries

    init_api_entries()


@manager.option('-e', '--env', type=str, dest="environ", required=False, default='dev')
def deploy(environ):
    from ops.deploy.deploy import deploy

    deploy(environ)


class CeleryCommand(Command):
    """execute celery"""

    def __init__(self):
        self.capture_all_args = True

    def run(self, *args, **kwargs):
        from api_x.task.tasks import app as celery
        from api_x.task import init_celery_app
        from api_x.config import api_celery_task as celery_config

        celery = init_celery_app(celery, celery_config, manager.app)
        celery.start(argv=['celery'] + args[0])

manager.add_command('celery', CeleryCommand())


@manager.option('-c', '--channel', type=str, dest="channel_name", required=True)
@manager.option('-e', '--entry', type=str, dest="entry_name", required=True)
def add_channel_perm(channel_name, entry_name):
    from api_x.zyt.user_mapping import add_perm_to_channel

    add_perm_to_channel(channel_name, entry_name)


@manager.option('-d', '--domain', type=str, dest="user_domain_name", required=True)
@manager.option('-u', '--user', type=str, dest="user_id", required=True)
def test_add_user(user_domain_name, user_id):
    from api_x.zyt.user_mapping import create_domain_account_user

    account_user_id = create_domain_account_user(user_domain_name, user_id)

    print('account_user_id: {0}'.format(account_user_id))


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
    pass


@manager.option('-i', '--id', type=long, dest="user_id", required=True)
@manager.option('-a', '--amount', type=Decimal, dest="amount", required=True)
@manager.option('-b', '--bankcard', type=int, dest="bankcard_id", required=True)
def test_withdraw(user_id, amount, bankcard_id):
    pass


@manager.option('-i', '--id', type=long, dest="withdraw_id", required=True)
@manager.option('-s', '--success', type=int, dest="success", default=1)
def test_done_withdraw(withdraw_id, success):
    from pytoolbox.util.dbs import require_transaction_context
    from api_x.zyt.biz.vas import get_vas_by_name
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
