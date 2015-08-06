# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import os

from flask import Flask


def register_mods(app):
    from old_api.index import index_mod
    from old_api.payment import pay_mod
    from old_api.refund import refund_mod
    from old_api.bankcard import card_mod
    from old_api.account import account_mod
    from old_api.client import client_mod

    app.register_blueprint(index_mod)
    app.register_blueprint(pay_mod)
    app.register_blueprint(refund_mod, url_prefix='/refund')
    app.register_blueprint(card_mod, url_prefix='/bankcards')
    app.register_blueprint(account_mod, url_prefix='/accounts')
    app.register_blueprint(client_mod, url_prefix='/clients')


def create_app(env):
    env = env.lower() if env else 'dev'
    os.environ['ENV'] = env

    app = Flask(__name__)
    register_mods(app)

    return app