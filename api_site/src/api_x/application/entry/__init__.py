# coding=utf-8
from __future__ import unicode_literals

from flask import Blueprint, render_template

application_mod = Blueprint('application', __name__)

from . import withdraw_views, bankcard_views, account_user_views, cheque_views


@application_mod.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=e), 404
