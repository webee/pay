# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import os

from flask import Flask
from pytoolbox.util import pmc_config
from pytoolbox.pay_client import PayClient


def register_mods(app):
    from sample_site.sample import sample_mod

    app.register_blueprint(sample_mod)


pay_client = PayClient()


def create_app(env='dev'):
    app = Flask(__name__)

    from sample_site import config
    os.environ['ENV'] = env
    pmc_config.register_config(config, env=env)

    app.config.from_object(config.App)
    register_mods(app)

    pay_client.init_config(config.PayClientConfig)

    return app
