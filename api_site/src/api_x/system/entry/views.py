# coding=utf-8
from __future__ import unicode_literals

from api_x.utils import response
from api_x.utils.entry_auth import verify_request
from . import system_entry_mod as mod, group
import time


@mod.route('/ping', methods=['GET'])
@group.verify_request('ping')
def ping():
    return response.success(msg="pong", t=time.time())


@mod.route('/test', methods=['GET'])
@group.verify_request('test')
def test():
    return response.success(msg="test", t=time.time())


@mod.route('/foo', methods=['GET'])
@verify_request('foo')
def foo():
    return response.success(msg="foo", t=time.time())
