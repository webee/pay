# -*- coding: utf-8 -*-
from flask import jsonify


def created(id):
    resp = jsonify({'id':id})
    resp.status_code = 201
    return resp
