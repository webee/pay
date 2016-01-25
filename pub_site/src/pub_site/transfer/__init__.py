# -*- coding: utf-8 -*-
from flask import Blueprint, g, request

transfer_mod = Blueprint('transfer', __name__, static_folder='static')

from . import views


@transfer_mod.before_request
def set_current_channel():
    g.current_channel = 'transfer'
