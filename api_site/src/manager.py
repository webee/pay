#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals, print_function

from flask.ext.script import Manager, Server
import sys

from api import create_app, config
from pytoolbox.util import dbe


manager = Manager(create_app)
manager.add_option('-e', '--env', dest='env', required=False)

server = Server(host="0.0.0.0", port=5000)
manager.add_command("runserver", server)


@manager.command
def init_db():
    from ops.deploy.init_db import init_db
    init_db()


def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')

    dbe.create_db_engine(config.DataBase.HOST, config.DataBase.PORT, config.DataBase.INSTANCE,
                         config.DataBase.USERNAME, config.DataBase.PASSWORD)
    manager.run()


if __name__ == '__main__':
    main()
