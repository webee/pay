# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import Blueprint

auth_mod = Blueprint('auth', __name__, template_folder='./templates', static_folder='static')


from . import views
