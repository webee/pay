# coding=utf-8
from __future__ import unicode_literals

import time
from flask import jsonify
from . import business_mod as mod


@mod.route('/', methods=['GET', 'POST'])
def index():
    return jsonify(ret=True, name='index', t=time.time())
