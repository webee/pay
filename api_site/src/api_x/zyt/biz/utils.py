# coding=utf-8
from __future__ import unicode_literals

from api_x.config import etc as config
from datetime import datetime
import random


def generate_sn(user_id):
    if config.Transaction.SN_PREFIX:
        prefix = config.Transaction.SN_PREFIX[:2]
        return prefix + datetime.now().strftime("%Y%m%d%H%M%S%f") + '%0.7d' % user_id + '%0.3d' % random.randint(0, 999)
    return datetime.now().strftime("%Y%m%d%H%M%S%f") + '%0.7d' % user_id + '%0.5d' % random.randint(0, 99999)
