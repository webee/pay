# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import Flask
from config import PAY_API_CONFIG


def register_mods(app):
    from api.payment import pay_mod

    app.register_blueprint(pay_mod)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(PAY_API_CONFIG[config_name])
    PAY_API_CONFIG[config_name].init_app(app)

    register_mods(app)

    return app
