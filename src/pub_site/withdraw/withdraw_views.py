# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from flask.ext.login import login_required, current_user
from flask import render_template, url_for, redirect, g
from . import withdraw_mod as mod
from tools.mylog import get_logger
from .forms import BindCardForm


logger = get_logger(__name__)


@mod.before_request
def set_current_channel():
    g.current_channel = 'withdraw'


@mod.route('/withdraw')
@login_required
def withdraw():
    return redirect(url_for('.bind_card'))


@mod.route('/withdraw/bind-card', methods=['GET', 'POST'])
@login_required
def bind_card():
    form = BindCardForm()
    if form.validate_on_submit():

        return redirect(url_for('.withdraw'))
    return render_template('bind-card.html', form=form)


@mod.route('/withdraw/<transaction_id>/result')
@login_required
def show_withdraw_result_page(transaction_id):
    return render_template('show-withdraw-result.html')