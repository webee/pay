# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import request, jsonify
from . import data_mod as mod
from tools.mylog import get_logger
from pub_site import config
import time

logger = get_logger(__name__)


@mod.route('/provinces')
def provinces():
    data = config.Data.PROVINCES_AND_CITIES

    provinces = [(p, pd['c']) for p, pd in data.items()]

    return jsonify(ret=True, data=provinces, version=time.time())


@mod.route('/provinces/<province_name>/cities')
def province_cities(province_name):
    data = config.Data.PROVINCES_AND_CITIES

    province = data.get(province_name)
    if province is None:
        return not_found()

    cities = [(c, cd['c']) for c, cd in province['cities'].items()]

    return jsonify(ret=True, data=cities, version=time.time())


def not_found():
    message = {
        'ret': False,
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp
