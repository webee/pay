# -*- coding: utf-8 -*-
from . import recon_mod as mod
from flask import render_template
import flask
from admin_site import flask_login, login_manager
from admin_site import config

users = {
    'yl': {'pw': 'lvye'},
    'op': {'pw': 'lvye123'}
}


class User(flask_login.UserMixin):
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
    if flask.request.method == 'GET':
        return render_template('reconciliation/login.html')
    username = flask.request.form['username']
    if flask.request.form['pw'] == users.get(username, {}).get('pw'):
        user = User()
        user.id = username
        flask_login.login_user(user)
        print 'redirect'
        return flask.redirect('/recon/')

    return render_template('reconciliation/login.html', tips=u"用户名或者密码错误")


@mod.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id


@mod.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'


@login_manager.unauthorized_handler
def unauthorized():
    return flask.redirect('/recon/login')


@mod.route('/', methods=['GET'])
@flask_login.login_required
def list_reconciliation():
    return render_template('reconciliation/list.html', config=_get_config())


@mod.route('/search', methods=['GET'])
@flask_login.login_required
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
