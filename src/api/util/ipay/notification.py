# -*- coding: utf-8 -*-
from flask import jsonify


class Notification(object):
    def is_invalid(self):
        return jsonify({'ret_code': '9999'})

    def duplicate(self):
        return jsonify({'ret_code': '0000', 'ret_msg': '重复通知'})

    def succeed(self):
        return jsonify({'ret_code': '0000', 'ret_msg': '交易成功'})

    def fail(self):
        return jsonify({'ret_code': '0000', 'ret_msg': '交易失败'})
