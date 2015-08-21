# -*- coding: utf-8 -*-
from flask import Blueprint


frontpage_mod = Blueprint('frontpage', __name__, static_folder='static')

from . import frontpage_views


