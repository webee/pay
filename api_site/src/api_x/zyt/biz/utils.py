# coding=utf-8
from __future__ import unicode_literals

from datetime import datetime
import random


def generate_sn(user_id):
    return datetime.now().strftime("%Y%m%d%H%M%S%f") + '%0.7d' % user_id + '%0.5d' % random.randint(0, 99999)
