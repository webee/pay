# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import request, jsonify
from . import data_mod as mod
from pytoolbox.util.log import get_logger
from pub_site import config
import time

logger = get_logger(__name__)


@mod.route('/provinces')
def provinces():
    data = [(key, value) for key, value in config.Data.PROVINCES.items()]
    return jsonify(ret=True, data=data, version=time.time())


@mod.route('/provinces/<province_code>/cities')
def province_cities(province_code):
    province = config.Data.CITIES.get(province_code)
    if province is None:
        return not_found()
    data = [(key, value) for key, value in province.items()]
    return jsonify(ret=True, data=data, version=time.time())


def not_found():
    message = {
        'ret': False,
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp
