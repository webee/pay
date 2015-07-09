#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals, print_function

import os

from flask.ext.script import Manager, Server
from lianlian_pay import create_app

app = create_app(os.getenv('SYSTEM_CONFIG') or 'default')
manager = Manager(app)


server = Server(host="0.0.0.0", port=8001)
manager.add_command("runserver", server)


if __name__ == '__main__':
    manager.run()
