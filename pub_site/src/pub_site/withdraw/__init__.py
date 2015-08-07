# -*- coding: utf-8 -*-
from flask import Blueprint

WITHDRAW_COMMISSION = 2

withdraw_mod = Blueprint('withdraw', __name__, static_folder='static')

from . import withdraw_views


