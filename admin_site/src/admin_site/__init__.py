# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

import os
from flask import Flask, render_template, current_app
from pytoolbox.util import dbe


def _init_template(app):
    @app.context_processor
    def register_context():
        return dict()

    app.jinja_options['extensions'].append('jinja2.ext.loopcontrols')


def _init_errors(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', error=e), 404

    @app.errorhandler(400)
    def request_error(e):
        current_app.error("internal server error.")
        return render_template('500.html', error=e), 500

    @app.errorhandler(500)
    def internal_server_error(e):
        current_app.error("internal server error.")
        return render_template('500.html', error=e), 500


def _register_mods(app):
    pass


def _init_csrf_protect(app):
    from flask_wtf.csrf import CsrfProtect
    csrf = CsrfProtect()
    csrf.init_app(app)


def create_app(env):
    from pytoolbox.conf import config as conf
    from admin_site import config

    app = Flask(__name__, template_folder='./templates')

    env = env or 'dev'
    os.environ['ENV'] = env
    conf.load(config, env=env)

    app.config.from_object(config.App)

    dbe.create_db_engine(config.DataBase.HOST, config.DataBase.PORT, config.DataBase.INSTANCE,
                         config.DataBase.USERNAME, config.DataBase.PASSWORD)
    _register_mods(app)
    _init_template(app)
    _init_errors(app)
    _init_csrf_protect(app)

    return app
