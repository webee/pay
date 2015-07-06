#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals, print_function

import os

from flask.ext.script import Manager, Shell

from pay_site import create_app

app = create_app(os.getenv('SYSTEM_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app)


manager.add_command("shell", Shell(make_context=make_shell_context))


#####################################
# 数据库相关
#####################################
@manager.command
def init_db():
    from deploy import init_db
    init_db()


@manager.command
def update_env():
    from deploy import update_env
    update_env


@manager.option('-u', '--user_id', dest="user_id", required=True)
@manager.option('-p', '--password', dest="password", required=True)
def add_user(user_id, password):
    print("add user %s." % user_id)


if __name__ == '__main__':
    manager.run()
