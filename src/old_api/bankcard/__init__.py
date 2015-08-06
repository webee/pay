# -*- coding: utf-8 -*-
from flask import Blueprint

card_mod = Blueprint('bankcard', __name__)

from . import views
