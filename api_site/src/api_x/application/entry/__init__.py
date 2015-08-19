# coding=utf-8
from __future__ import unicode_literals

from flask import Blueprint, render_template

application_mod = Blueprint('application', __name__, template_folder='./templates')


from api_x.application.entry import views, withdraw_views

@application_mod.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=e), 404
