# coding=utf-8
from __future__ import unicode_literals

from flask import Blueprint, render_template

biz_entry_mod = Blueprint('biz_entry', __name__, template_folder='./templates')

from . import views, pay_views, refund_views, withdraw_views


@biz_entry_mod.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=e), 404
