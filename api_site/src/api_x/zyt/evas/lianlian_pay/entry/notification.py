# coding=utf-8
from __future__ import unicode_literals

from flask import jsonify


def is_invalid():
    return jsonify({'ret_code': '9999'})


def duplicate():
    return jsonify({'ret_code': '0000', 'ret_msg': '重复通知'})


def succeed():
    return jsonify({'ret_code': '0000', 'ret_msg': '交易成功'})


def fail():
    return jsonify({'ret_code': '0000', 'ret_msg': '交易失败'})


def accepted():
    return jsonify({'ret_code': '0000', 'ret_msg': 'accepted'})


def refused():
    return jsonify({'ret_code': '9999', 'ret_msg': 'refused'})
