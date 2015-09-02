#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals, print_function

from flask.ext.script import Manager, Shell, Server, Command
from flask.ext.migrate import MigrateCommand
from api_x import create_app
from ops.deploy.deploy import deploy, db_migrate


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


@manager.command
def deploy_prod():
    deploy('prod', 'pay_api_site')

@manager.command
def deploy_beta():
    deploy('beta', 'pay_api_site', do_deploy=False)


@manager.option('-e', '--env', type=str, dest="environ", required=False, default='dev')
def deploy_celery(environ):
    deploy(environ, 'pay_api_celery')


@manager.option('-e', '--env', type=str, dest="environ", required=False, default='dev')
def migrate_db(environ):
    db_migrate(environ)


class CeleryCommand(Command):
    """execute celery"""

    def __init__(self):
        self.capture_all_args = True

    def run(self, *args, **kwargs):
        from api_x.task import celery

        celery.start(argv=['celery'] + args[0])

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


if __name__ == '__main__':
    manager.run()
