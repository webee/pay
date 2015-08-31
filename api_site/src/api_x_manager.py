#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals, print_function
from decimal import Decimal

from flask.ext.script import Manager, Shell, Server, Command
from flask.ext.migrate import MigrateCommand
from api_x import create_app


manager = Manager(create_app)
manager.add_option('-e', '--env', dest='env', default='dev', required=False)
manager.add_option('-d', '--deploy', action='store_true', dest='deploy', required=False, default=False)

manager.add_command('db', MigrateCommand)


def make_shell_context():
    import api_x
    from api_x import config, db
    from api_x.task import tasks

    return dict(api=api_x, app=manager.app, config=config, db=db, tasks=tasks, manager=manager)


manager.add_command("shell", Shell(make_context=make_shell_context))

server = Server(host="0.0.0.0", port=5100)
manager.add_command("runserver", server)


@manager.option('-r', '--recreate', action="store_true", dest="recreate", required=False, default=False)
@manager.option('-d', '--drop_all', action="store_true", dest="drop_all", required=False, default=False)
def init_db(recreate, drop_all):
    from fabric.api import local
    from api_x import db
    from api_x.data import init_data
    from api_x.zyt.user_mapping import update_api_entries

    def recreate_db():
        from pytoolbox.util.console_log import info

        info('recreating database ...')
        local('mysql -u root -p < db/init_db.sql')

    if recreate:
        recreate_db()
    if drop_all:
        db.drop_all()
    db.create_all()

    update_api_entries()
    init_data()


@manager.command
def update_api_entry():
    from api_x.zyt.user_mapping import update_api_entries

    update_api_entries()


@manager.option('-e', '--env', type=str, dest="environ", required=False, default='dev')
def deploy(environ):
    from ops.deploy.deploy import deploy

    deploy(environ, 'pay_api_site')


@manager.option('-e', '--env', type=str, dest="environ", required=False, default='dev')
def deploy_celery(environ):
    from ops.deploy.deploy import deploy

    deploy(environ, 'pay_api_celery')


class CeleryCommand(Command):
    """execute celery"""

    def __init__(self):
        self.capture_all_args = True

    def run(self, *args, **kwargs):
        from api_x.task import tasks

        tasks.app.start(argv=['celery'] + args[0])

manager.add_command('celery', CeleryCommand())


@manager.option('-c', '--channel', type=str, dest="channel_name", required=True)
@manager.option('-e', '--entry', type=str, dest="entry_name", required=True)
def add_channel_perm(channel_name, entry_name):
    from api_x.zyt.user_mapping import add_perm_to_channel

    add_perm_to_channel(channel_name, entry_name)


@manager.option('-d', '--domain', type=str, dest="domain_name", required=True)
@manager.option('-u', '--user', type=str, dest="user_id", required=True)
def open_domain_user(domain_name, user_id):
    from api_x.zyt.user_mapping import set_user_is_opened

    set_user_is_opened(domain_name, user_id, True)


@manager.option('-d', '--domain', type=str, dest="domain_name", required=True)
@manager.option('-u', '--user', type=str, dest="user_id", required=True)
def close_domain_user(domain_name, user_id):
    from api_x.zyt.user_mapping import set_user_is_opened

    set_user_is_opened(domain_name, user_id, False)


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
