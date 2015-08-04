# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import Flask, render_template
from flask.ext.login import LoginManager
from tools.filters import register_filters, register_global_functions
from tools import pmc_config


def init_template(app):
    @app.context_processor
    def register_context():
        return dict()

    app.jinja_options['extensions'].append('jinja2.ext.loopcontrols')
    register_filters(app)
    register_global_functions(app)


def init_errors(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', error=e), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html', error=e), 500


def register_mods(app):
    from pub_site.withdraw import withdraw_mod
    from pub_site.user import user_mod

    app.register_blueprint(withdraw_mod)
    app.register_blueprint(user_mod)


# extensions.
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'user.login'
login_manager.login_message = None


def create_app(env='dev'):
    app = Flask(__name__, template_folder='./templates')

    from pub_site import config
    pmc_config.register_config(config, env=env)

    app.config.from_object(config)

    register_mods(app)
    init_template(app)
    init_errors(app)

    return app
