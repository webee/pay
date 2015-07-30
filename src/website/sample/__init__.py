# -*- coding: utf-8 -*-
from flask import Blueprint

sample_mod = Blueprint('sample', __name__, template_folder='./templates', static_folder='static')

from website.sample import views, withdraw_views, callback_views
