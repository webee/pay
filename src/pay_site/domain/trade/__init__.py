# -*- coding: utf-8 -*-
from trade import mod

def register_trade_module(app):
    app.register_blueprint(mod)