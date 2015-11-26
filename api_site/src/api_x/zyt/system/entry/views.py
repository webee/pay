# coding=utf-8
from __future__ import unicode_literals

from api_x.utils import response
from api_x.utils.entry_auth import verify_request
from . import system_entry_mod as mod
import time


@mod.route('/ping', methods=['GET'])
@verify_request(['ping', 'system'])
def ping():
    return response.success(msg="pong", t=time.time())


@mod.route('/test', methods=['GET'])
@verify_request(['test', 'system'])
def test():
    return response.success(msg="test", t=time.time())
