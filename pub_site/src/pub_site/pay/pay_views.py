# -*- coding: utf-8 -*-

from flask import g, render_template
from flask.ext.login import login_required,current_user
from .import pay_mod as mod

@mod.before_request
def set_current_channel():
    g.current_channel = 'pay'


@mod.route('/pay', methods=['GET', 'POST'])
@login_required
def pay():
    return render_template('pay/pay.html')