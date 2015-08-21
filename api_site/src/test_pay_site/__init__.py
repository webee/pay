# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import os

from flask import Flask
from pytoolbox.util import pmc_config


def register_mods(app):
    from test_pay_site.main import main_mod

    app.register_blueprint(main_mod)


def create_app(env='dev'):
    app = Flask(__name__)

    from test_pay_site import config
    os.environ['ENV'] = env
    pmc_config.register_config(config, env=env)

    app.config.from_object(config.App)
    register_mods(app)

    return app
