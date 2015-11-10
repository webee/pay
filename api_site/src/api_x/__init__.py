# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import os

from flask import Flask
from flask.ext.migrate import Migrate
from flask.ext.qrcode import QRcode
from pytoolbox.util import dbs
from pytoolbox.util.dbs import db


# extensions
migrate = Migrate()
qrcode = QRcode()


def register_mods(app):
    from api_x.main import main_mod
    from api_x.zyt.entry import biz_entry_mod
    from api_x.zyt.user_mapping.entry import user_mapping_entry_mod
    from api_x.zyt.vas.entry import vas_entry_mod
    from api_x.zyt.evas.test_pay.entry import test_pay_entry_mod
    from api_x.zyt.evas.lianlian_pay.entry import lianlian_pay_entry_mod
    from api_x.zyt.evas.weixin_pay.entry import weixin_pay_entry_mod

    app.register_blueprint(main_mod)
    app.register_blueprint(biz_entry_mod, url_prefix='/biz')
    app.register_blueprint(user_mapping_entry_mod, url_prefix='/user_mapping')
    app.register_blueprint(vas_entry_mod, url_prefix='/vas/zyt')
    app.register_blueprint(test_pay_entry_mod, url_prefix="/vas/test_pay")
    app.register_blueprint(lianlian_pay_entry_mod, url_prefix="/vas/lianlian_pay")
    app.register_blueprint(weixin_pay_entry_mod, url_prefix="/vas/weixin_pay")

    from api_x.application.entry import application_mod
    app.register_blueprint(application_mod, url_prefix="/application")


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
    from api_x.application import models

    dbs.init_db(app)
    db.init_app(app)

    migrate.init_app(app, db)

    qrcode.init_app(app)


def init_tasks(app):
    from api_x.task import celery
    from api_x.task import init_celery_app
    from api_x.config import api_celery_task as celery_config

    init_celery_app(celery, celery_config, app)


def custom_flask(app):
    from flask.json import JSONEncoder
    from datetime import datetime

    class CustomJSONEncoder(JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat(sep=str(' '))
            return super(CustomJSONEncoder, self).default(obj)
    app.json_encoder = CustomJSONEncoder


def create_app(env='dev', deploy=False):
    if deploy:
        return Flask(__name__)

    app = Flask(__name__)

    # 最先初始化配置
    init_config(app, env)

    register_mods(app)
    init_extensions(app)
    custom_flask(app)

    from api_x.zyt.biz import init_register_notify_handles
    init_register_notify_handles()

    from api_x.zyt import evas
    evas.init()

    init_tasks(app)

    init_template(app)

    return app


def init_template(app):
    @app.context_processor
    def register_context():
        from api_x import config
        return dict(
            CONFIG=config
        )

    app.jinja_options['extensions'].append('jinja2.ext.loopcontrols')
    register_filters(app)
    register_global_functions(app)


def register_filters(app):
    from api_x.utils import times
    app.jinja_env.filters['utc2gmt8'] = times.utc2gmt8


def register_global_functions(app):
    from api_x.config import etc
    from flask import url_for

    def abs_url_for(*args, **kwargs):
        return etc.HOST_URL + url_for(*args, **kwargs)

    app.jinja_env.globals['abs_url_for'] = abs_url_for
