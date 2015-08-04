# -*- coding: utf-8 -*-
from flask import Blueprint, g

main_mod = Blueprint('main', __name__, static_folder='static')

from . import views


@main_mod.before_request
def set_current_channel():
    g.current_channel = 'main'
