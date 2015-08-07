# -*- coding: utf-8 -*-
from flask import Blueprint

pay_mod = Blueprint('pay', __name__, static_folder='static')

from . import pay_views


