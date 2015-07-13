#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals, print_function

import os

from flask.ext.script import Manager, Shell, Server
from api import create_app


app = create_app(os.getenv('SYSTEM_CONFIG') or 'default')
manager = Manager(app)

def make_shell_context():
    return dict(app=app)
manager.add_command("shell", Shell(make_context=make_shell_context))

server = Server(host="0.0.0.0", port=5000)
manager.add_command("runserver", server)

@manager.command
def init_db():
    from ops.deploy.init_db import init_db
    init_db()


if __name__ == '__main__':
    manager.run()
