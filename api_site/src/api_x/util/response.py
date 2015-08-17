# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from flask import Response, jsonify
import decimal
import datetime


def success(**kwargs):
    return jsonify(ret=True, **kwargs)


def fail(code, msg, **kwargs):
    return jsonify(ret=False, code=code, msg=msg, **kwargs)


def updated(ids):
    return ok(ids=ids)


def list_data(items):
    js = _dumps(items)
    return Response(js, status=200, mimetype='application/json')


def ok(*args, **kwargs):
    if len(args) > 0:
        return _response(200, args[0])
    return _response(200, kwargs)


def created(id):
    return _response(201, {'id': id})


def accepted(id):
    return _response(202, {'id': id})


def not_found(params=None):
    return _response(404, {'error': 'not found', 'params': params})


def bad_request(message, **request_params):
    return _response(400, {'error': message, 'params': str(request_params)})


def _response(status_code, obj=None):
    js = _dumps(obj if obj else {})
    return Response(js, status=status_code, mimetype='application/json')


def _dumps(obj):
    return json.dumps(obj, cls=_DecimalEncoder)


class _DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        return super(_DecimalEncoder, self).default(o)
