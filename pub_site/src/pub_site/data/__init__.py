# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import Blueprint

data_mod = Blueprint('data', __name__, url_prefix='/data', template_folder='./templates', static_folder='static')


from . import views
