# -*- coding: utf-8 -*-
def register_mods(app):
    from .entry import entry_mod
    from .trade import trade_mod

    app.register_blueprint(entry_mod)
    app.register_blueprint(trade_mod, url_prefix='/trade')
