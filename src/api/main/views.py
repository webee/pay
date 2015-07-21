# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division


from . import main_mod as mod
from flask import render_template


@mod.route('/')
def index():
    return render_template('index.html')
