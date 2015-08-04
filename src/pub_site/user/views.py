# coding=utf-8
from __future__ import unicode_literals, print_function

from flask import request, redirect, url_for
from flask.ext.login import login_user, logout_user, login_required
from . import user_mod as mod
from pub_site.utils.urls import build_url
from .models import load_user
from pub_site import config


@mod.route('/login')
def login():
    next_url = request.args.get('next', '/')
    url = build_url(config.AccountCenter.LOGIN_URL, client_id=config.AccountCenter.CLIENT_ID, next=next_url)
    return redirect(url)


@mod.route('/auth', methods=['GET', 'POST'])
def auth():
    data = request.values

    code = data['code']
    state = data['state']

    # TODO: xxx
    # get ref.
    # verify user by codea/state, and get user id.
    verify_url = config.AccountCenter.VERIFY_URL
    ref = '/'
    user_id = None
    user = load_user(user_id)
    if user is not None:
        login_user(user)
        return redirect(ref)
    return redirect(url_for('.login'))


@mod.route('/logout')
@login_required
def logout():
    logout_user()

    return redirect(url_for('user.login'))
