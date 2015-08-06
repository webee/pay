#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from flask.ext.script import Manager, Server
import sys

from website import create_app


manager = Manager(create_app)
manager.add_option('-e', '--env', dest='env', required=False)

server = Server(host="0.0.0.0", port=5001)
manager.add_command("runserver", server)


def main():
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    manager.run()


if __name__ == '__main__':
    main()
