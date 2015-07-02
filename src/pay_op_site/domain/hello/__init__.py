# -*- coding: utf-8 -*-
from hello import mod

def register_hello_module(app):
    app.register_blueprint(mod)