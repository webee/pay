# -*- coding: utf-8 -*-
from flask import jsonify, abort


def created(id):
    resp = jsonify({'id':id})
    resp.status_code = 201
    return resp


def not_found():
    return abort(404)