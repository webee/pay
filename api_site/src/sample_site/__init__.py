# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import os

from flask import Flask
from tools import pmc_config


def register_mods(app):
    from sample_site.sample import sample_mod

    app.register_blueprint(sample_mod, url_prefix='/sample')


def create_app(env='dev'):
    app = Flask(__name__)

    from sample_site import config
    os.environ['ENV'] = env
    pmc_config.register_config(config, env=env)

    app.config.from_object(config.App)
    register_mods(app)

    return app
