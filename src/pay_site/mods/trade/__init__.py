# -*- coding: utf-8 -*-
from flask import Blueprint

trade_mod = Blueprint('trade', __name__, template_folder='', static_folder='static')

from . import views
