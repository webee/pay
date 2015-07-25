# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import Flask

from app_config import PAY_API_CONFIG


def register_mods(app):
    from api.index import index_mod
    from api.payment import pay_mod
    from api.refund import refund_mod
    from api.bankcard import card_mod
    from api.account import account_mod

    app.register_blueprint(index_mod)
    app.register_blueprint(pay_mod)
    app.register_blueprint(refund_mod, url_prefix='/refund')
    app.register_blueprint(card_mod, url_prefix='/bankcards')
    app.register_blueprint(account_mod, url_prefix='/accounts')


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(PAY_API_CONFIG[config_name])
    PAY_API_CONFIG[config_name].init_app(app)

    register_mods(app)

    return app
