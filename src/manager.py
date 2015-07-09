#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals, print_function

from flask import Flask
from flask.ext.script import Manager

import pay_api_manager as pay_api
import pay_manager as pay


manager = Manager(Flask(__name__))
manager.add_command("pay_api", pay_api.manager)
manager.add_command("pay", pay.manager)

#####################################
# 数据库相关
#####################################
@manager.command
def init_db():
    from ops.deploy import init_db
    init_db()

    pay.init_db()


@manager.command
def update_env():
    from ops.deploy import update_env
    update_env()


if __name__ == '__main__':
    manager.run()
