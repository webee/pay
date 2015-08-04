# coding=utf-8
from __future__ import unicode_literals, print_function
from flask.ext.login import UserMixin, AnonymousUserMixin
from pub_site import login_manager


class User(UserMixin):
    VERIFY_API = 'http://qsso.corp.qunar.com/api/verifytoken.php'

    def __init__(self, id, username, phone_num):
        self.id = id
        self.username = username
        self.phone_num = phone_num

    def __repr__(self):
        return '<User %r>' % self.id


class AnonymousUser(AnonymousUserMixin):
    pass


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    # TODO: xx
    # fetch user info by user id.
    return None

