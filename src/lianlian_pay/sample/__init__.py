# -*- coding: utf-8 -*-
from flask import Blueprint

sample_mod = Blueprint('sample', __name__, template_folder='./templates', static_folder='static')

from . import views