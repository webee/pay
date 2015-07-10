# -*- coding: utf-8 -*-
from flask import Blueprint

pay_mod = Blueprint('payment', __name__)

from . import views
