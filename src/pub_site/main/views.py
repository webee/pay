# coding=utf-8
from __future__ import unicode_literals
from flask import request, render_template
from flask.ext.login import login_required
from . import main_mod as mod


@mod.route('/', methods=['GET'])
@login_required
def index():
    return render_template('main/index.html')
