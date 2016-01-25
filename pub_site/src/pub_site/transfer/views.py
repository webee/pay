# coding=utf-8
from __future__ import unicode_literals
from flask import render_template, flash, redirect, url_for
from flask.ext.login import current_user
from . import transfer_mod as mod
from .forms import TransferForm
from decimal import Decimal
from pub_site import pay_client
from pub_site.models import LvyeAccount
from pub_site.auth.utils import login_required


@mod.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = TransferForm()
    user_id = current_user.user_id
    if form.validate_on_submit():
        username = form.username.data
        lvye_account = LvyeAccount.query.filter_by(username=username).first()
        amount = Decimal(form.amount.data)
        info = form.info.data
        res = pay_client.user_transfer(user_id, 'lvye_account', lvye_account.user_id, amount, info)
        if res:
            flash('转账成功', category='success')
            return redirect(url_for('main.index'))
        flash('转账失败', category='error')
    return render_template('transfer/index.html', form=form,
                           balance='%.2f' % pay_client.app_query_user_available_balance(user_id))
