# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import request, redirect, session, url_for, jsonify
from flask_login import UserMixin, AnonymousUserMixin, login_user, logout_user, login_required, current_user

from . import auth_mod as mod
from pytoolbox.util.log import get_logger
from pub_site import login_manager
from pub_site import config
from tools.urls import build_url

logger = get_logger(__name__)


class User(UserMixin):
    def __init__(self, xid, user_id, user_name, is_leader, phone_no):
        self.id = xid
        self.user_id = user_id
        self.user_name = user_name
        self.is_leader = is_leader
        self.phone_no = phone_no

    def to_dict(self):
        return dict(id=self.id, user_id=self.user_id, user_name=self.user_name,
                    is_leader=self.is_leader, phone_no=self.phone_no)

    @classmethod
    def from_json(cls, user_json, cookie_id):
        xid = cookie_id
        user_id = int(user_json.get('uid'))
        user_name = user_json.get('username')
        is_leader = user_json.get('isleader') == "1"
        phone_no = user_json.get('phone')

        return User(xid, user_id, user_name, is_leader, phone_no)

    @classmethod
    def from_dict(cls, user_dict):
        xid = user_dict.get('id')
        user_id = user_dict.get('user_id')
        user_name = user_dict.get('user_name')
        is_leader = user_dict.get('is_leader')
        phone_no = user_dict.get('phone_no')
        return User(xid, user_id, user_name, is_leader, phone_no)

    @classmethod
    def get(cls, xid):
        import urllib2
        import json
        url = config.UserCenter.IS_PASSPORT_LOGIN_URL
        req = urllib2.Request(
            url=url,
            headers={'Content-Type': 'text/xml', 'Cookie': config.UserCenter.AUTH_COOKIE + "=%s" % xid},
        )
        try:
            txt = urllib2.urlopen(req, timeout=3).read()
            logger.warn('user json: ' + txt)
            user_json = json.loads(txt.strip()[5:-1])
            return User.from_json(user_json, xid)

        except Exception as _:
            logger.exception(_)
            return None


class AnonymousUser(AnonymousUserMixin):
    pass


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.from_dict(session.get('current_user'))


@mod.route('/login/')
def login():
    next_url = request.args.get('next', url_for('main.index'))

    auth_url = build_url(config.HOST_URL + config.URL_MOUNT_PREFIX + url_for('auth.auth'), next=next_url)
    login_url = build_url(config.UserCenter.PASSPORT_LOGIN_URL, refererUrl=auth_url)
    return redirect(login_url)


@mod.route('/auth/')
def auth():
    user_cookie = request.cookies.get(config.UserCenter.AUTH_COOKIE)
    user = User.get(user_cookie)
    logger.info('user cookie: {}, user: {}'.format(user_cookie, user))
    if user is not None:
        login_user(user)
        session['current_user'] = user.to_dict()

    next_url = request.args.get('next') or url_for('main.index')
    return redirect(next_url)


@mod.route('/logout/')
@login_required
def logout():
    logout_user()
    session.clear()

    return redirect(config.UserCenter.LOGOUT_URL)


@mod.route('/info/')
@login_required
def info():
    user = current_user._get_current_object()

    return jsonify(**(user.to_dict()))
