# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from . import frontpage_mod as mod
from flask import render_template, redirect, url_for
from flask.ext.login import current_user, login_required
from pytoolbox.util.log import get_logger
from . import dba


log = get_logger(__name__)


@mod.route('/')
def main():
    return render_template('frontpage/main.html')


@mod.route('/application')
@login_required
def application():
    if not current_user.is_leader:
        return render_template('frontpage/user_is_not_allowed.html')
    user_domain_name = current_user.user_domain_name
    user_id = current_user.user_id
    user_name = current_user.user_name
    _ = dba.add_leader_application(user_domain_name, user_id, user_name)
    return redirect(url_for('.application_success'))


@mod.route('/application_success')
@login_required
def application_success():
    return render_template('frontpage/application_success.html')
