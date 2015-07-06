# -*- coding: utf-8 -*-
from flask import Blueprint

entry_mod = Blueprint('entry', __name__, template_folder='./templates', static_folder='static')

from pay_site.entry import views
