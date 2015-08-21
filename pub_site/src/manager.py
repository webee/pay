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
    from pub_site import config
    return dict(app=manager.app, config=config)


manager.add_command("shell", Shell(make_context=make_shell_context))

server = Server(host="0.0.0.0", port=5002)
manager.add_command("runserver", server)


@manager.command
def migrate():
    from ops.deploy.migration import do_migration
    do_migration()


@manager.option('-e', '--env', type=str, dest="envx", required=False, default='dev')
@manager.option('-r', '--recreate', action="store_true", dest="recreate", required=False, default=False)
def init_db(envx, recreate):
    from ops.deploy.init_db import init_db

    init_db(envx, recreate)


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
