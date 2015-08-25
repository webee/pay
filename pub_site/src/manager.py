#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import sys

from flask.ext.script import Manager, Server, Shell
from pub_site import create_app


manager = Manager(create_app)
manager.add_option('-e', '--env', dest='env', required=False, default='dev')
manager.add_option('-d', '--deploy', action='store_true', dest='deploy', required=False, default=False)


def make_shell_context():
    from pub_site import config, db
    return dict(app=manager.app, config=config, db=db)


manager.add_command("shell", Shell(make_context=make_shell_context))

server = Server(host="0.0.0.0", port=5102)
manager.add_command("runserver", server)


@manager.command
def migrate():
    from ops.deploy.migration import do_migration
    do_migration()


@manager.option('-r', '--recreate', action="store_true", dest="recreate", required=False, default=False)
def init_db(recreate):
    from fabric.api import local
    from pub_site import db

    def recreate_db():
        from pytoolbox.util.console_log import info

        info('recreating database ...')
        local('mysql -u root -p < migration/init_db.sql')

    if recreate:
        recreate_db()
    db.drop_all()
    db.create_all()


@manager.option('-e', '--env', type=str, dest="env", required=True, default='dev')
def deploy(env):
    from ops.deploy.deploy import deploy
    deploy(env)


def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    manager.run()


if __name__ == '__main__':
    main()
