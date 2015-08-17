# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import os

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


def register_mods(app):
    from api_x.zyt.entry import entry_mod
    from api_x.zyt.evas.test_pay.entry import test_pay_entry_mod
    from api_x.zyt.evas.lianlian_pay.entry import lianlian_pay_entry_mod

    app.register_blueprint(entry_mod)
    app.register_blueprint(test_pay_entry_mod, url_prefix="/vas/test_pay")
    app.register_blueprint(lianlian_pay_entry_mod, url_prefix="/vas/lianlian_pay")


def init_config(app, env):
    from api_x import config

    env = env or 'dev'
    os.environ['ENV'] = env
    config.load_config(env)

    from api_x.config import etc as config
    app.config.from_object(config.App)


def init_extensions(app):
    from api_x.zyt.biz import models
    from api_x.zyt.vas import models
    from api_x.zyt.user_mapping import models

    db.init_app(app)


def custom_flask(app):
    from flask.json import JSONEncoder
    from datetime import datetime

    class CustomJSONEncoder(JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat(sep=str(' '))
            return super(CustomJSONEncoder, self).default(obj)
    app.json_encoder = CustomJSONEncoder


# extensions.
db = SQLAlchemy(session_options={'autocommit': True})


def create_app(env):
    app = Flask(__name__)

    init_config(app, env)
    register_mods(app)
    init_extensions(app)
    custom_flask(app)

    from api_x.zyt.biz import init_register_notify_handles
    init_register_notify_handles()

    return app
