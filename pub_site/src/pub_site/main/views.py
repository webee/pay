# coding=utf-8
from __future__ import unicode_literals
from flask import request, render_template
from flask.ext.login import login_required, current_user
from . import main_mod as mod
from pub_site import pay_client


@mod.route('/', methods=['GET'])
@login_required
def index():
    uid = current_user.user_id
    balance = pay_client.get_user_balance(uid)
    cash_records = pay_client.get_user_cash_records(uid)

    res = {
        'balance': balance,
        'cash_records': cash_records
    }
    return render_template('main/index.html', res=res)
