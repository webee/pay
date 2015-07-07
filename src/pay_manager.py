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
    from ops.deploy import init_db
    from tools.dbi import from_db, require_transaction_context
    from pay_site.entry import client_info
    init_db()

    with require_transaction_context():
        db = from_db()
        db.insert('client_info', name='TEST', client_id=client_info.client_id, key_value=client_info.key_value)


@manager.command
def update_env():
    from ops.deploy import update_env
    update_env()


@manager.option('-u', '--user_id', dest="user_id", required=True)
@manager.option('-p', '--password', dest="password", required=True)
def add_user(user_id, password):
    print("add user %s." % user_id)


if __name__ == '__main__':
    manager.run()
