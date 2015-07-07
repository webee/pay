# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import Flask, render_template
from config import PAY_CONFIG
from tools.filters import register_filters, register_global_functions


def init_template(app):
    """
    初始化模板相关
    :type app: flask.app.Flask
    :return:
    """
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
    from pay_site.entry import entry_mod
    from pay_site.trade import trade_mod
    from pay_site.lvye import lvye_mod
    from pay_site.account import account_mod

    app.register_blueprint(entry_mod)
    app.register_blueprint(trade_mod, url_prefix='/trade')
    app.register_blueprint(lvye_mod, url_prefix='/lvye')
    app.register_blueprint(account_mod, url_prefix='/account')


def create_app(config_name):
    app = Flask(__name__, template_folder='./templates')
    app.config.from_object(PAY_CONFIG[config_name])
    PAY_CONFIG[config_name].init_app(app)

    register_mods(app)
    init_template(app)
    init_errors(app)

    return app
