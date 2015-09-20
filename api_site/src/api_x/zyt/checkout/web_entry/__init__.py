# coding=utf-8
from __future__ import unicode_literals

from flask import Blueprint, render_template

web_checkout_entry_mod = Blueprint('web_checkout_entry', __name__, template_folder='./templates')

from . import views


@web_checkout_entry_mod.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=e), 404
