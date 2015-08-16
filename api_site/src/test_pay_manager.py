#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from flask.ext.script import Manager, Server, Shell
from test_pay_site import create_app


manager = Manager(create_app)
manager.add_option('-e', '--env', dest='env', default='dev', required=False)


def make_shell_context():
    import sample_site
    from sample_site import config
    return dict(website=sample_site, app=manager.app, config=config)


manager.add_command("shell", Shell(make_context=make_shell_context))

server = Server(host="0.0.0.0", port=8090)
manager.add_command("runserver", server)


if __name__ == '__main__':
    manager.run()
