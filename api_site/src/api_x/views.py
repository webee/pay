# coding=utf-8
from __future__ import unicode_literals

from api_x.config import etc as config
from flask import Blueprint, jsonify
import time

main_mod = Blueprint('main', __name__)

@main_mod.route('/ping')
def ping():
    return jsonify(env=config.__env_name__,
                   host_url=config.HOST_URL,
                   t=time.time())
