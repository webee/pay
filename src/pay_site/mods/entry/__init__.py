# -*- coding: utf-8 -*-
from flask import Blueprint

entry_mod = Blueprint('entry', __name__, template_folder='', static_folder='static')

from . import views
