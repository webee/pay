# -*- coding: utf-8 -*-
from flask import Blueprint

account_mod = Blueprint('account', __name__, template_folder='./templates', static_folder='static')

from . import views
