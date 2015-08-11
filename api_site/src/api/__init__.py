# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from flask import Flask
import os
from api.delegation_center import delegate, event
from api.direct_transaction import delegation_interface as direct_delegate
from api.secured_transaction import delegation_interface as secured_delegate
from pytoolbox.conf import config as conf
from pytoolbox.util import dbe


def register_mods(app):
    from api.facade_views import mod
    from api.core_views import core_mod
    from api.secured_transaction_views import secured_mod
    from api.direct_transaction_views import direct_mod
    from api.transaction_log_views import transaction_log_mod

    app.register_blueprint(mod)
    app.register_blueprint(secured_mod, url_prefix='/secured')
    app.register_blueprint(direct_mod, url_prefix='/direct')
    app.register_blueprint(core_mod, url_prefix='/core')
    app.register_blueprint(transaction_log_mod)


def register_callbacks():
    delegate.bind_secured_handler(event.PAY, secured_delegate.pay_by_id)
    delegate.bind_direct_handler(event.PAY, direct_delegate.pay_by_id)

    delegate.bind_secured_handler(event.PAID, secured_delegate.guarantee_payment)
    delegate.bind_direct_handler(event.PAID, direct_delegate.update_payment_to_be_success)

    delegate.bind_secured_handler(event.REDIRECT_WEB_AFTER_PAID, secured_delegate.get_sync_callback_url_of_payment)
    delegate.bind_direct_handler(event.REDIRECT_WEB_AFTER_PAID, direct_delegate.get_sync_callback_url_of_payment)

    delegate.bind_secured_handler(event.REFUNDED, secured_delegate.after_refunded)


def create_app(env):
    app = Flask(__name__)

    from api import config
    env = env or 'dev'
    os.environ['ENV'] = env
    conf.load(config, env=env)

    dbe.create_db_engine(config.DataBase.HOST, config.DataBase.PORT, config.DataBase.INSTANCE,
                         config.DataBase.USERNAME, config.DataBase.PASSWORD)

    register_mods(app)
    register_callbacks()

    return app
