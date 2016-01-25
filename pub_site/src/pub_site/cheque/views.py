# coding=utf-8
from __future__ import unicode_literals
from flask import render_template
from . import cheque_mod as mod
from pub_site.auth.utils import login_required


@mod.route('/', methods=['GET'], defaults={'path': ''})
@mod.route('/<path:path>', methods=['GET'])
@login_required
def index(path):
    return render_template('cheque/index.html')
