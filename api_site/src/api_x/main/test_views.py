# coding=utf-8
from __future__ import unicode_literals

from flask import jsonify, request
from . import main_mod as mod
import time
from api_x.utils import req


@mod.route('/test/client_type')
def client_type():
    user_agent = request.user_agent.string
    return jsonify(user_agent=user_agent,
                   client_type=req.client_type(),
                   t=time.time())
