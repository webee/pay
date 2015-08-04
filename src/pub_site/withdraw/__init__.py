# -*- coding: utf-8 -*-
from flask import Blueprint

withdraw_mod = Blueprint('withdraw', __name__, template_folder='./templates', static_folder='static')

from . import withdraw_views
