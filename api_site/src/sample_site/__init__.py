# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import os

from flask import Flask
from pytoolbox.util import pmc_config
from pytoolbox.pay_client import PayClient
from pytoolbox.util.flask.utils import ReverseProxied


def register_mods(app):
    from sample_site.sample import sample_mod
    from sample_site.app_server import app_server_mod

    app.register_blueprint(sample_mod)
    app.register_blueprint(app_server_mod, url_prefix="/app")


pay_client = PayClient()


def create_app(env='dev'):
    app = Flask(__name__)

    from sample_site import config
    os.environ['ENV'] = env
    pmc_config.register_config(config, env=env)

    app.config.from_object(config.App)
    register_mods(app)

    pay_client.init_config(config.PayClientConfig)

    # reverse proxied
    app.wsgi_app = ReverseProxied(app.wsgi_app)
    return app

