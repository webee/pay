# -*- coding: utf-8 -*-
from flask import jsonify, abort


def created(id):
    return _response(201, {'id': id})


def accepted(id):
    return _response(202, {'id': id})


def not_found():
    return _response(404)


def bad_request(message, **request_params):
    return _response(400, {'error': message, 'params': str(request_params)})


def _response(status_code, obj=None):
    resp = jsonify(obj if obj else {})
    resp.status_code = status_code
    return resp
