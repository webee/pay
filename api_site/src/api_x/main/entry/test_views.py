# coding=utf-8
from __future__ import unicode_literals

from flask import jsonify, request
from . import main_entry_mod as mod
import time
from api_x.utils import req


@mod.route('/test/client_type')
def client_type():
    user_agent = request.user_agent.string
    return jsonify(user_agent=user_agent,
                   client_type=req.client_type(),
                   t=time.time())


@mod.route('/test/ip', methods=['GET'])
def ip():
    x_real_ip = request.headers.get('X-Real-IP')
    x_forwarded_for = request.headers.get('X-Forwarded-For')

    return jsonify(remote_addr=request.remote_addr,
                   x_real_ip=x_real_ip,
                   x_forwarded_for=x_forwarded_for)
