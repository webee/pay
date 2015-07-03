# coding=utf-8
from __future__ import unicode_literals
from __future__ import print_function
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
from pay_site import create_app

app = create_app(os.getenv('SYSTEM_CONFIG') or 'production')
