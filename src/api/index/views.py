# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from . import index_mod as mod
from flask import render_template, redirect


@mod.route('/')
def index():
    return redirect('http://huodong.lvye.com')
    # return render_template('index.html')
