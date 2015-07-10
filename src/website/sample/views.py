# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import render_template
from . import sample_mod as mod
from tools.mylog import get_logger

logger = get_logger(__name__)


@mod.route('/')
def index():
    return render_template('omnipotent.html')

@mod.route('/pay-one-cent', methods=['POST'])
def pay_one_cent():
    return render_template('omnipotent.html', pay_result='SUCCESS')
