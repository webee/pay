# -*- coding: utf-8 -*-
from flask import Blueprint

pay_mod = Blueprint('payment', __name__, template_folder='./templates', static_folder='static')

from . import views
