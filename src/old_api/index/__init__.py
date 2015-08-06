# -*- coding: utf-8 -*-
from flask import Blueprint

index_mod = Blueprint('main', __name__)

from . import views
