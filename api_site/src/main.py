# coding=utf-8
from __future__ import unicode_literals, print_function
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
from api import create_app

app = create_app(os.getenv('ENV') or 'prod')