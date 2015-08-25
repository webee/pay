# coding=utf-8
from __future__ import unicode_literals

from functools import wraps
from flask import redirect, render_template, url_for
from flask.ext.login import current_user, login_required as _login_required
from .dba import is_leader_applied
from pub_site import pay_client


def require_leader_and_is_opened(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = current_user
        if not user.is_leader:
            return render_template('frontpage/user_is_not_allowed.html')

        if not is_leader_applied(user.user_domain_name, user.user_id):
            # 没有申请的，则到申请页面
            return redirect(url_for('frontpage.main') + '#leader-application')
        # 已申请
        data = pay_client.query_user_is_opened(user.user_id)
        if not (data and data['is_opened']):
            # 未开通
            return redirect(url_for('frontpage.application_success'))
        # 已开通
        return f(*args, **kwargs)
    return wrapper


def login_required(f):
    return _login_required(require_leader_and_is_opened(f))
