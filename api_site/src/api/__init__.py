# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from flask import Flask
import os
from pytoolbox import conf


def register_mods(app):
    from api.facade_views import mod
    from api.core_views import core_mod
    from api.secured_transaction_views import secured_mod
    from api.transaction_log_views import transaction_log_mod

    app.register_blueprint(mod)
    app.register_blueprint(secured_mod, url_prefix='/secured')
    app.register_blueprint(core_mod, url_prefix='/core')
    app.register_blueprint(transaction_log_mod)


def create_app(env):
    app = Flask(__name__)

    from api import config
    env = env or 'dev'
    os.environ['ENV'] = env
    conf.load(config, env=env)

    register_mods(app)

    return app
