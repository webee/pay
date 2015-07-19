# coding=utf-8
from functools import wraps
from flask import jsonify


def return_json(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        return jsonify(func(*args, **kwargs))
    return wrap
