# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from pytoolbox.migrate import migrate


def do_migration():
    migrate.migrate('migration')
