# coding=utf-8
from __future__ import unicode_literals


class response(object):
    INVALID_NOTIFICATION = {'ret_code': '9999'}
    NOTIFIED = {'ret_code': '0000', 'ret_msg': '重复通知'}
    SUCCESS = {'ret_code': '0000', 'ret_msg': '交易成功'}
    FAILURE = {'ret_code': '0000', 'ret_msg': '交易失败'}
