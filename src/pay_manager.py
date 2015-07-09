#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals, print_function

import os

from flask.ext.script import Manager, Shell, Server

from pay_site import create_app, test_client_info

app = create_app(os.getenv('SYSTEM_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app)


manager.add_command("shell", Shell(make_context=make_shell_context))
server = Server(host="0.0.0.0", port=5001)
manager.add_command("runserver", server)


#####################################
# 数据库相关
#####################################
@manager.command
def init_db():
    from tools.dbi import from_db, require_transaction_context
    from pay_site import test_client_info

    # 准备测试数据
    with require_transaction_context():
        db = from_db()
        db.insert('client_info', name='TEST', client_id=test_client_info.client_id)
        db.insert('account', id=test_client_info.to_account_id, user_source='lvye', user_id='webee')


if __name__ == '__main__':
    manager.run()
