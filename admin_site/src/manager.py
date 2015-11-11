#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import sys

from flask.ext.script import Manager, Server, Shell
from admin_site import create_app
from ops.deploy.deploy import deploy

manager = Manager(create_app)
manager.add_option('-e', '--env', dest='env', required=False)
manager.add_option('-d', '--deploy', action='store_true', dest='deploy', required=False, default=False)


def make_shell_context():
    from admin_site import config
    return dict(app=manager.app, config=config)


manager.add_command("shell", Shell(make_context=make_shell_context))

server = Server(host="0.0.0.0", port=5104)
manager.add_command("runserver", server)


@manager.option('-u', '--update_only', action="store_true", dest="update_only", required=False, default=False)
def deploy_prod(update_only):
    deploy('prod', 'pay_admin_site', do_deploy=not update_only)


@manager.command
def deploy_beta():
    deploy('beta', 'pay_admin_site', do_deploy=False)


def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    manager.run()


if __name__ == '__main__':
    main()
