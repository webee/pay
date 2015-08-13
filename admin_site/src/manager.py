#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import sys

from flask.ext.script import Manager, Server, Shell
from admin_site import create_app

manager = Manager(create_app)
manager.add_option('-e', '--env', dest='env', required=False)


def make_shell_context():
    from admin_site import config
    return dict(app=manager.app, config=config)


manager.add_command("shell", Shell(make_context=make_shell_context))

server = Server(host="0.0.0.0", port=5004)
manager.add_command("runserver", server)


def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    manager.run()


if __name__ == '__main__':
    main()
