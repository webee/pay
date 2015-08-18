# coding=utf-8
from __future__ import unicode_literals

from flask import jsonify


def succeed():
    return jsonify({'ret_code': '0000', 'ret_msg': 'success'})


def failed():
    return jsonify({'ret_code': '9999'})


def duplicate():
    """重复通知, 不再通知"""
    return succeed()


def bad():
    return succeed()


def miss():
    """没有处理, 期待下次发送处理"""
    return failed()
