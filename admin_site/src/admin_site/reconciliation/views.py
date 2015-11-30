# -*- coding: utf-8 -*-
from . import recon_mod as mod
from flask import request, render_template, url_for, redirect
from flask.ext.login import login_required, UserMixin, login_user, logout_user, current_user
from admin_site import login_manager
from admin_site import config

users = {
    'yl': {'pw': 'lvye'},
    'op': {'pw': 'lvye123'}
}


class User(UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['pw'] == users[email]['pw']

    return user


@mod.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('reconciliation/login.html')
    username = request.form['username']
    if request.form['pw'] == users.get(username, {}).get('pw'):
        user = User()
        user.id = username
        login_user(user)
        return redirect(config.HOST_URL + url_for('reconciliation.list_reconciliation'))

    return render_template('reconciliation/login.html', tips=u"用户名或者密码错误")


@mod.route('/protected')
@login_required
def protected():
    return 'Logged in as: ' + current_user.id


@mod.route('/logout')
def logout():
    logout_user()
    return 'Logged out'


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(config.HOST_URL + url_for('reconciliation.login'))


@mod.route('/', methods=['GET'])
@login_required
def list_reconciliation():
    return render_template('reconciliation/list.html', config=_get_config())


@mod.route('/search', methods=['GET'])
@login_required
def search_transaction():
    return render_template('reconciliation/search.html', config=_get_config())


def _get_config():
    return compose_conf(
        apiHost=config.Host.API_SITE
    )


def compose_conf(**kwargs):
    conf = {}
    for key, value in kwargs.iteritems():
        key = key.encode('ascii')
        value = value.encode('ascii')
        conf[key] = value

    return conf
