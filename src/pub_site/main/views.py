# coding=utf-8
from __future__ import unicode_literals
from flask import request, render_template
from flask.ext.login import login_required, current_user
from . import main_mod as mod
from pub_site import config
import requests


@mod.route('/', methods=['GET'])
@login_required
def index():
    uid = current_user.user_id
    get_user_balance_url = config.PayAPI.GET_USER_BALANCE_URL.format(user_domain_id=config.USER_DOMAIN_ID, user_id=uid)
    req = requests.get(get_user_balance_url)
    data = req.json()
    res = {
        'balance': data['balance']
    }
    return render_template('main/index.html', res=res)
