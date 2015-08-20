# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import request, redirect, session, url_for
from flask_login import UserMixin, AnonymousUserMixin, login_user, logout_user, login_required

from . import auth_mod as mod
from pytoolbox.util.log import get_logger
from pub_site import login_manager
from pub_site import config
from tools.urls import build_url

logger = get_logger(__name__)


class User(UserMixin):
    def to_dict(self):
        return dict(id=self.id, user_id=self.user_id, user_name=self.user_name, is_leader=self.is_leader)

    @classmethod
    def from_json(cls, user_json, cookie_id):
        user = User()
        user.id = cookie_id
        user.user_id = user_json.get('uid')
        user.user_name = user_json.get('username')
        user.is_leader = user_json.get('isleader')
        return user

    @classmethod
    def from_dict(cls, user_dict):
        user = User()
        user.id = user_dict.get('id')
        user.user_id = user_dict.get('user_id')
        user.user_name = user_dict.get('user_name')
        user.is_leader = user_dict.get('is_leader')
        return user

    @classmethod
    def get(cls, id):
        import urllib2
        import json
        url = config.UserCenter.IS_PASSPORT_LOGIN_URL
        logger.info(' url: {}'.format(url))
        request = urllib2.Request(
            url=url,
            headers={'Content-Type': 'text/xml', 'Cookie': config.UserCenter.AUTH_COOKIE + "=%s" % id},
        )
        try:
            txt = urllib2.urlopen(request, timeout=3).read()
            logger.warn('user json: ' + txt)
            user_json = json.loads(txt.strip()[5:-1])
            return User.from_json(user_json, id)

        except Exception as _:
            logger.exception(_)
            return None


class AnonymousUser(AnonymousUserMixin):
    pass


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.from_dict(session.get('current_user'))


@mod.route('/auth/login/')
def login():
    next_url = request.args.get('next', '/')

    auth_url = build_url(config.HOST_URL + url_for('auth.auth'), next=next_url)
    login_url = build_url(config.UserCenter.PASSPORT_LOGIN_URL, refererUrl=auth_url)
    return redirect(login_url)


@mod.route('/auth/auth/')
def auth():
    user_cookie = request.cookies.get(config.UserCenter.AUTH_COOKIE)
    user = User.get(user_cookie)
    logger.info('user cookie: {}, user: {}'.format(user_cookie, user))
    if user is not None:
        login_user(user)
        session['current_user'] = user.to_dict()

    next_url = request.args.get('next') or '/'
    return redirect(next_url)


@mod.route('/auth/logout/')
@login_required
def logout():
    logout_user()
    session.clear()

    return redirect(config.UserCenter.LOGOUT_URL)
