#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals, print_function

import os

from flask.ext.script import Manager, Shell, Server
from pay_api import create_app

app = create_app(os.getenv('SYSTEM_CONFIG') or 'default')
manager = Manager(app)


manager.add_command("shell", Shell(make_context=dict(app=app)))
server = Server(host="0.0.0.0", port=5000)
manager.add_command("runserver", server)


if __name__ == '__main__':
    manager.run()
