# coding=utf-8
from __future__ import unicode_literals
from __future__ import print_function
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
from importlib import import_module

site = import_module(os.getenv('SITE', 'api'))

app = site.create_app(os.getenv('SYSTEM_CONFIG') or 'production')
