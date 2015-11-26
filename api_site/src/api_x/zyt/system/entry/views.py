# coding=utf-8
from __future__ import unicode_literals

from api_x.utils import response
from . import system_entry_mod as mod
import time


@mod.route('/ping', methods=['GET'])
def ping():
    return response.success(msg="pong", t=time.time())
