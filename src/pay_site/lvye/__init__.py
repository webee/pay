# -*- coding: utf-8 -*-
from flask import Blueprint

lvye_mod = Blueprint('lvye', __name__, template_folder='', static_folder='static')

from pay_site.lvye import views
