# coding=utf-8
from __future__ import unicode_literals
from flask import jsonify
from . import api_mod as mod


@mod.route('/test', methods=['GET', 'POST'])
def test():
    return jsonify(ret='ok')
