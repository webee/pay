# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import os

from flask import Flask
from pytoolbox.util import pmc_config
from pytoolbox.pay_client import PayClient


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


class ReverseProxied(object):
    """Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)
