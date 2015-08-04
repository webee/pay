# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from flask.ext.login import login_required, current_user
from flask import render_template, url_for, redirect, g
from . import withdraw_mod as mod
from tools.mylog import get_logger
from .forms import BindCardForm
from identifying_code_manager import generate_and_send


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
        return redirect(url_for('.bind_card_succeed'))
    return render_template('withdraw/bind-card.html', form=form)


@mod.route('/withdraw/bind-card-succeed', methods=['GET'])
@login_required
def bind_card_succeed():
    return render_template('withdraw/bind-card-succeed.html')


@mod.route('/withdraw/<transaction_id>/result')
@login_required
def show_withdraw_result_page(transaction_id):
    return render_template('withdraw/show-withdraw-result.html')


@mod.route('/withdraw/generate-identifying-code', methods=['POST'])
@login_required
def generate_identifying_code():
    resp = generate_and_send()
    return resp.content, resp.status_code