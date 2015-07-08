# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import Flask
from config import PAY_API_CONFIG


def register_mods(app):
    from pay_api.account import account_mod
    from pay_api.trade import trade_mod

    app.register_blueprint(account_mod, url_prefix='/account')
    app.register_blueprint(account_mod, url_prefix='/trade')


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(PAY_API_CONFIG[config_name])
    PAY_API_CONFIG[config_name].init_app(app)

    register_mods(app)

    return app
