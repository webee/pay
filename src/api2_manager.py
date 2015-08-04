#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals, print_function

from flask.ext.script import Manager, Server

from api2 import create_app


manager = Manager(create_app)
manager.add_option('-e', '--env', dest='env', required=False)

server = Server(host="0.0.0.0", port=5100)
manager.add_command("runserver", server)


@manager.command
def init_db():
    from ops.deploy.init_db import init_db_2
    init_db_2()


if __name__ == '__main__':
    manager.run()
