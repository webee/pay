#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import sys

from flask.ext.script import Manager, Server, Shell
from flask.ext.migrate import MigrateCommand
from pub_site import create_app
from ops.deploy.deploy import deploy


manager = Manager(create_app)
manager.add_option('-e', '--env', dest='env', required=False, default='dev')
manager.add_option('-d', '--deploy', action='store_true', dest='deploy', required=False, default=False)

manager.add_command('db', MigrateCommand)


def make_shell_context():
    from pub_site import config, db
    return dict(app=manager.app, config=config, db=db)


manager.add_command("shell", Shell(make_context=make_shell_context))

server = Server(host="0.0.0.0", port=5102)
manager.add_command("runserver", server)


@manager.option('-r', '--recreate', action="store_true", dest="recreate", required=False, default=False)
@manager.option('-d', '--drop_all', action="store_true", dest="drop_all", required=False, default=False)
def init_db(recreate, drop_all):
    from fabric.api import local
    from pub_site import db

    def recreate_db():
        from pytoolbox.util.console_log import info

        info('recreating database ...')
        local('mysql -u root -p < db/init_db.sql')

    if recreate:
        recreate_db()
    if drop_all:
        db.drop_all()
    db.create_all()


@manager.option('-u', '--update_only', action="store_true", dest="update_only", required=False, default=False)
def deploy_prod(update_only):
    deploy('prod', 'pay_pub_site', do_deploy=not update_only)


@manager.command
def deploy_beta():
    deploy('beta', 'pay_pub_site', do_deploy=False)


@manager.option('-m', '--minutes', type=long, dest="minutes", required=True, default=10)
def fetch_withdraw_result_notify(minutes):
    from pub_site.notify import task

    task.fetch_notify_withdraw_result(minutes)


@manager.option('-d', '--user_domain', type=str, dest="user_domain_name", required=True)
@manager.option('-u', '--username', type=str, dest="username", required=True)
@manager.option('-p', '--phone', type=str, dest="phone", required=True)
@manager.option('-P', '--password', type=str, dest="password", required=True)
def add_domain_user(user_domain_name, username, phone, password):
    from pub_site.auth.dba import add_domain_user

    user_id = add_domain_user(user_domain_name, username, phone, password)
    print('user_id: [{0}]'.format(user_id))


def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    manager.run()


if __name__ == '__main__':
    main()
