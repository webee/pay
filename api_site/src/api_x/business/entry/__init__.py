# coding=utf-8
from __future__ import unicode_literals
from api_x.business.entry import views

from flask import Blueprint, render_template

business_mod = Blueprint('business', __name__, template_folder='./templates')


@business_mod.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=e), 404
