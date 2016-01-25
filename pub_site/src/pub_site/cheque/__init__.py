# -*- coding: utf-8 -*-
from flask import Blueprint, g, request

cheque_mod = Blueprint('cheque', __name__, static_folder='static')

from . import views


@cheque_mod.before_request
def set_current_channel():
    g.current_channel = 'cheque'
    endpoint = request.endpoint.split('.')[1]
    g.current_cheque_tab = endpoint
