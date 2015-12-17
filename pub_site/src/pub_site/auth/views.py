# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import request, redirect, session, url_for, jsonify, render_template, flash
from flask import after_this_request
from flask_login import UserMixin, AnonymousUserMixin, login_user, logout_user, login_required, current_user

from . import auth_mod as mod
from pytoolbox.util.log import get_logger
from pub_site import login_manager
from pub_site import config
from pytoolbox.util.urls import build_url
from pub_site.auth.models import DomainUser
from .lvye_corp_login_forms import LvyeCorpLoginForm

logger = get_logger(__name__)


class User(UserMixin):
    def __init__(self, xid, user_id, user_name, is_leader, phone_no, channel_name):
        self.id = xid
        self.user_id = user_id
        self.user_name = user_name
        self.is_leader = is_leader
        self.phone_no = phone_no
        self.channel_name = channel_name

    def to_dict(self):
        return dict(id=self.id, user_id=self.user_id, user_name=self.user_name,
                    is_leader=self.is_leader, phone_no=self.phone_no, channel_name=self.channel_name)

    @classmethod
    def from_lvye_account_json(cls, user_json, cookie_id):
        xid = cookie_id
        user_id = int(user_json.get('uid'))
        user_name = user_json.get('username')
        is_leader = user_json.get('isleader') == "1"
        phone_no = user_json.get('phone')
        channel_name = config.LvyePaySitePayClientConfig.CHANNEL_NAME

        return User(xid, user_id, user_name, is_leader, phone_no, channel_name)

    @classmethod
    def from_dict(cls, user_dict):
        xid = user_dict.get('id')
        user_id = user_dict.get('user_id')
        user_name = user_dict.get('user_name')
        is_leader = user_dict.get('is_leader')
        phone_no = user_dict.get('phone_no')
        channel_name = user_dict.get('channel_name')
        return User(xid, user_id, user_name, is_leader, phone_no, channel_name)

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
            return User.from_lvye_account_json(user_json, xid)

        except Exception as _:
            logger.exception(_)
            return None

    def __repr__(self):
        return str(self.to_dict())


class AnonymousUser(AnonymousUserMixin):
    pass


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.from_dict(session.get('current_user'))


@mod.route('/login/', methods=["GET", "POST"])
def login():
    next_url = request.args.get('next')
    channel_name = request.args.get('channel', request.cookies.get('channel', config.DEFAULT_CHANNEL))
    if current_user.is_authenticated() and current_user.channel_name == channel_name:
        return redirect(next_url)

    @after_this_request
    def remember_channel_name(response):
        response.set_cookie('channel', channel_name)
        return response

    if channel_name == config.LvyePaySitePayClientConfig.CHANNEL_NAME:
        # 绿野用户中心
        next_url = next_url or url_for('main.index')
        auth_url = build_url(config.HOST_URL + url_for('auth.auth'), next=next_url)
        login_url = build_url(config.UserCenter.PASSPORT_LOGIN_URL, refererUrl=auth_url)
        return redirect(login_url)
    elif channel_name == config.LvyeCorpPaySitePayClientConfig.CHANNEL_NAME:
        user_domain_name = 'lvye_corp'
        # 绿野公司
        form = LvyeCorpLoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            domain_user = DomainUser.query.filter_by(user_domain_name=user_domain_name, username=username).first()
            if domain_user is not None and domain_user.verify_password(password):
                # login user.
                is_leader = True
                user = User(domain_user.id, domain_user.username, domain_user.username, is_leader,
                            domain_user.phone, channel_name)
                do_login_user(user)
                next_url = next_url or url_for('main.index')
                return redirect(next_url)
            flash('用户名或密码错误', category='error')
        return render_template('auth/lvye_corp_login.html', channel=channel_name, form=form, next=next_url)
    return render_template('info.html', msg="错误的登录")


def do_login_user(user):
    login_user(user)
    session['current_user'] = user.to_dict()


def do_logout_user():
    logout_user()
    session.clear()


@mod.route('/auth/')
def auth():
    user_cookie = request.cookies.get(config.UserCenter.AUTH_COOKIE)
    user = User.get(user_cookie)
    logger.info('user cookie: {}, user: {}'.format(user_cookie, user))
    if user is not None:
        do_login_user(user)

    next_url = request.args.get('next', url_for('main.index'))
    return redirect(next_url)


@mod.route('/logout/')
@login_required
def logout():
    channel_name = current_user.channel_name
    do_logout_user()

    next_url = request.referrer or config.HOST_URL + url_for('main.index')
    if channel_name == config.DEFAULT_CHANNEL:
        return redirect(config.UserCenter.LOGOUT_URL + '?next=' + next_url)
    return redirect(url_for('auth.login', next=next_url, channel=channel_name))


@mod.route('/info/')
@login_required
def info():
    user = current_user._get_current_object()

    return jsonify(**(user.to_dict()))
