# coding=utf-8
from functools import wraps
from flask import current_app, jsonify
from flask.ext.login import current_user
from . import response


class SubBlueprint(object):
    def __init__(self, name, blueprint, url_prefix=''):
        self.name = name
        self.blueprint = blueprint
        self.url_prefix = url_prefix

    def route(self, orig_rule, **options):
        def decorator(f):
            endpoint = options.pop("endpoint", f.__name__)

            rule = self.url_prefix + orig_rule
            endpoint = '%s:%s' % (self.name, endpoint)
            self.blueprint.add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator

    def __getattr__(self, item):
        if item == 'add_url_rule':
            return self.add_url_rule
        return getattr(self.blueprint, item)


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not current_user.is_authenticated():
            return response.failed('login required', need_login=True)
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view
