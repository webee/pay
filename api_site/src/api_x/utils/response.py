# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from flask import Response, jsonify
import decimal
import datetime


def success(**kwargs):
    return jsonify(ret=True, **kwargs)


def fail(code=1, msg='fail', **kwargs):
    return jsonify(ret=False, code=code, msg=msg, **kwargs)


def bad_request(code=1, msg='bad request', **kwargs):
    return fail(code, msg, **kwargs), 400


def not_found(code=404, msg='not found.', **kwargs):
    return fail(code, msg, **kwargs), 404


def accepted(**kwargs):
    return success(**kwargs), 202
