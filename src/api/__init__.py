# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from flask import Flask
import os


def register_mods(app):
    from api.facade_views import mod
    from api.core_views import core_mod
    from api.secured_transaction_views import secured_mod

    app.register_blueprint(mod)
    app.register_blueprint(secured_mod, url_prefix='/secured')
    app.register_blueprint(core_mod, url_prefix='/core')


def create_app(env):
    env = env.lower() if env else 'dev'
    os.environ['ENV'] = env

    app = Flask(__name__)
    register_mods(app)

    return app
