# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import Blueprint, request, redirect, session
from flask_login import UserMixin, AnonymousUserMixin, login_user

from tools.mylog import get_logger
from pub_site import login_manager

mod = Blueprint('login', __name__, template_folder='./templates', static_folder='static')

logger = get_logger(__name__)


class User(UserMixin):

    def to_dict(self):
        return dict(id=self.id, user_id=self.user_id, user_name=self.user_name, is_leader=self.is_leader)

    @classmethod
    def from_json(cls, user_json, cookie_id):
        user = User()
        user.id=cookie_id
        user.user_id=user_json.get('uid')
        user.user_name=user_json.get('username')
        user.is_leader=user_json.get('isleader')
        return user

    @classmethod
    def from_dict(cls, user_dict):
        user = User()
        user.id= user_dict.get('id')
        user.user_id= user_dict.get('user_id')
        user.user_name= user_dict.get('user_name')
        user.is_leader= user_dict.get('is_leader')
        return user

    @classmethod
    def get(cls, id):
        import urllib2, json
        url = "http://api.passport.lvye.com/header/islogin.shtml"
        request = urllib2.Request(
            url=url,
            headers={'Content-Type': 'text/xml', 'Cookie': "4a7e7f902968e79c8b4e4975f316eb65=%s" % id},
        )
        try:
            txt = urllib2.urlopen(request, timeout=3).read()
            logger.warn('user json: '+txt)
            user_json = json.loads(txt.strip()[5:-1])
            return User.from_json(user_json, id)

        except Exception, e:
            return None


class AnonymousUser(AnonymousUserMixin):
    pass

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.from_dict(session.get('current_user'))


@mod.route('/login')
def do_login_action():
    next_url = request.args.get('next', '/')
    return redirect('http://api.passport.lvye.com/oauth/toLogin/?refererUrl=http://pay.lvye.com:5002/login/success?next='+next_url)


@mod.route('/login/success')
def on_login_success():
    user_cookie = request.cookies.get('4a7e7f902968e79c8b4e4975f316eb65')
    user = User.get(user_cookie)
    login_user(user)
    session['current_user']=user.to_dict()
    return redirect(request.args.get('next'))
