# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from flask.ext.login import login_required,current_user
from flask import render_template, url_for, redirect, g
from . import withdraw_mod as mod
from pytoolbox.util.dbe import from_db
from tools.mylog import get_logger
from .forms import BindCardForm
from identifying_code_manager import generate_and_send_identifying_code
from pay_client import PayClient
from flask import flash


logger = get_logger(__name__)


@mod.before_request
def set_current_channel():
    g.current_channel = 'withdraw'


@mod.route('/withdraw')
@login_required
def withdraw():
    result = PayClient().get_bankcards()
    if len(result['data']) == 0:
        return redirect(url_for('.bind_card'))
    return render_template('withdraw/withdraw.html')


@mod.route('/withdraw/bind-card', methods=['GET', 'POST'])
@login_required
def bind_card():
    form = BindCardForm()
    if form.validate_on_submit():
        card_number = form.card_number.data
        account_name = form.name.data
        province_code = form.province.data
        city_code = form.city.data
        branch_bank_name = form.subbranch_name.data
        result = PayClient().bind_bankcards(
            card_number=card_number,
            account_name=account_name,
            province_code=province_code,
            city_code=city_code,
            branch_bank_name=branch_bank_name
        )
        if result['status_code'] != 201:
            flash(result['data']['message'])
            return redirect(url_for('.bind_card'))
        _update_preferred_card(result['data']['id'])
        return redirect(url_for('.withdraw'))
    return render_template('withdraw/bind-card.html', form=form)


@mod.route('/withdraw/<transaction_id>/result')
@login_required
def show_withdraw_result_page(transaction_id):
    return render_template('withdraw/show-withdraw-result.html')


@mod.route('/withdraw/generate-identifying-code', methods=['POST'])
@login_required
def generate_identifying_code():
    resp = generate_and_send_identifying_code()
    return resp.content, resp.status_code


def _update_preferred_card(card_id):
    db = from_db()
    current_user_id = current_user.user_id
    user_id = db.exists('select user_id from preferred_card where user_id=%(user_id)s', user_id=current_user_id)
    if user_id == 0:
        db.insert('preferred_card', {"user_id": current_user_id, "bankcard_id": card_id})
    else:
        db.execute('update preferred_card set bankcard_id=%(card_id)s where user_id=%(user_id)s',
                   card_id=card_id, user_id=current_user_id)