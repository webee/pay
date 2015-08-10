# -*- coding: utf-8 -*-

from flask import g, render_template,redirect, url_for, flash
from flask.ext.login import login_required
from .import pay_mod as mod
from pub_site.pay.forms import PayForm


@mod.before_request
def set_current_channel():
    g.current_channel = 'pay'


@mod.route('/pay', methods=['GET', 'POST'])
@login_required
def pay():
    form = PayForm()
    if form.validate_on_submit():
        flash(u"付款给绿野支付成功！", category="success")
        return redirect(url_for('main.index'))
    return render_template('pay/pay.html', form=form)