# -*- coding: utf-8 -*-
from flask import jsonify, abort


def created(id):
    resp = jsonify({'id': id})
    resp.status_code = 201
    return resp


def accepted(id):
    resp = jsonify({'id': id})
    resp.status_code = 202
    return resp


def not_found():
    resp = jsonify({})
    resp.status_code = 404
    return resp


def bad_request(message, **request_params):
    resp = jsonify({'error': message, 'params': str(request_params)})
    resp.status_code = 400
    return resp
