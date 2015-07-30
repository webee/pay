# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import render_template
from . import sample_mod as mod


@mod.route('/callback-params')
def show_pay_result():
    return render_template('post_pay_result.html')