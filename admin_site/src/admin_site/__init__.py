# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

import os
from flask import Flask

import flask.ext.login as flask_login

login_manager = flask_login.LoginManager()


def _init_template(app):
    @app.context_processor
    def register_context():
        return dict()

    app.jinja_options['extensions'].append('jinja2.ext.loopcontrols')


def _register_mods(app):
    from admin_site.reconciliation import recon_mod

    app.register_blueprint(recon_mod, url_prefix='/recon')


def create_app(env="dev"):
    from pytoolbox.util import pmc_config
    from admin_site import config

    app = Flask(__name__, template_folder='./templates')

    env = env or 'dev'
    os.environ['ENV'] = env
    pmc_config.register_config(config, env=env)
    app.config.from_object(config.App)

    _register_mods(app)
    _init_template(app)
    login_manager.init_app(app)

    return app
