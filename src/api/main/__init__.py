# -*- coding: utf-8 -*-
from flask import Blueprint

main_mod = Blueprint('main', __name__, template_folder='./templates', static_folder='static')

from . import views