# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import Flask
from config import PAY_CONFIG


def register_mods(app):
    from pay_site.account import account_mod

    app.register_blueprint(account_mod, url_prefix='/account')


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(PAY_CONFIG[config_name])
    PAY_CONFIG[config_name].init_app(app)

    register_mods(app)

    return app
