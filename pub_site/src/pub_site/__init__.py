# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from datetime import timedelta

import os
from flask import Flask, render_template
from flask.ext.login import LoginManager, current_user
from flask.ext.migrate import Migrate
from flask.ext.wtf.csrf import CsrfProtect
from flask.ext.cors import CORS
from flask.ext.qrcode import QRcode
from tools.filters import register_filters, register_global_functions
from pytoolbox.pay_client import PayClient
from pytoolbox.util import dbs
from pytoolbox.util.dbs import db
from pytoolbox.util.log import get_logger
from pytoolbox.util.flask_extras.utils import ReverseProxied
from pub_site import config


logger = get_logger(__name__)

# extensions
migrate = Migrate()
qrcode = QRcode()


def init_template(app):
    @app.context_processor
    def register_context():
        from pub_site import config
        return dict(
            CONFIG=config
        )

    app.jinja_options['extensions'].append('jinja2.ext.loopcontrols')
    register_filters(app)
    register_global_functions(app)


def init_errors(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', error=e), 404

    @app.errorhandler(400)
    def request_error(e):
        logger.exception(e)
        return render_template('500.html', error=e), 500

    @app.errorhandler(500)
    def internal_server_error(e):
        logger.exception(e)
        return render_template('500.html', error=e), 500


def register_mods(app):
    from pub_site.auth import auth_mod
    from pub_site.main import main_mod
    from pub_site.sms import sms_mod
    from pub_site.withdraw import withdraw_mod
    from pub_site.cheque import cheque_mod
    from pub_site.data import data_mod
    from pub_site.pay_to_lvye import pay_to_lvye_mod
    from pub_site.frontpage import frontpage_mod
    from pub_site.notify import notify_mod
    from pub_site.checkout import checkout_entry_mod
    from pub_site.api import api_mod

    app.register_blueprint(auth_mod, url_prefix='/auth')
    app.register_blueprint(main_mod)
    app.register_blueprint(sms_mod, url_prefix='/sms')
    app.register_blueprint(withdraw_mod)
    app.register_blueprint(cheque_mod, url_prefix='/cheque')
    app.register_blueprint(data_mod)
    app.register_blueprint(pay_to_lvye_mod)
    app.register_blueprint(frontpage_mod)
    app.register_blueprint(notify_mod, url_prefix='/notify')
    app.register_blueprint(checkout_entry_mod, url_prefix='/checkout')
    app.register_blueprint(api_mod, url_prefix='/api')

    # exempt api
    csrf.exempt(notify_mod)
    csrf.exempt(api_mod)

    # cors
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


def init_config(app, env):
    from pytoolbox.conf import config as conf
    from pub_site import config

    env = env or 'dev'
    os.environ['ENV'] = env
    conf.load(config, env=env)

    app.config.from_object(config.App)


def init_extensions(app):
    from pub_site import models
    from pub_site.auth import models

    dbs.init_db(app)
    db.init_app(app)

    login_manager.init_app(app)
    csrf.init_app(app)

    migrate.init_app(app, db)
    qrcode.init_app(app)


def init_pay_clients(_pay_clients):
    _pay_clients[config.LvyePaySitePayClientConfig.CHANNEL_NAME] = PayClient(config.LvyePaySitePayClientConfig)
    _pay_clients[config.LvyeCorpPaySitePayClientConfig.CHANNEL_NAME] = PayClient(config.LvyeCorpPaySitePayClientConfig)

    _pay_clients[config.DEFAULT_CHANNEL].setup_accepted_clients(_pay_clients.values())


def custom_flask(app):
    from flask.json import JSONEncoder
    from datetime import datetime

    class CustomJSONEncoder(JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat(sep=str(' '))
            return super(CustomJSONEncoder, self).default(obj)
    app.json_encoder = CustomJSONEncoder
    app.permanent_session_lifetime = timedelta(minutes=10)


class CurrentPayClient(object):
    def __init__(self, _pay_clients):
        self._pay_clients = _pay_clients

    def __getattr__(self, item):
        channel_name = config.DEFAULT_CHANNEL
        try:
            channel_name = current_user.channel_name
        except:
            pass
        cur_pay_client = self._pay_clients[channel_name]
        return getattr(cur_pay_client, item)


# extensions.
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.login_message = None

csrf = CsrfProtect()
pay_clients = {}
pay_client = CurrentPayClient(pay_clients)


def create_app(env='dev', deploy=False):
    if deploy:
        return Flask(__name__)

    app = Flask(__name__)

    init_config(app, env)
    init_pay_clients(pay_clients)
    register_mods(app)
    init_extensions(app)
    custom_flask(app)

    init_template(app)
    init_errors(app)

    # reverse proxied
    app.wsgi_app = ReverseProxied(app.wsgi_app)
    return app
