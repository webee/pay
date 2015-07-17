# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import render_template, redirect
from . import sample_mod as mod
from tools.mylog import get_logger


logger = get_logger(__name__)


@mod.route('/withdraw')
def withdraw():
    return render_template('withdraw.html')


@mod.route('/do_withdraw', methods=['POST'])
def do_withdraw():
    pass
