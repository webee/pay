# -*- coding: utf-8 -*-
from flask import Blueprint

client_mod = Blueprint('client', __name__)

from . import views
