# -*- coding: utf-8 -*-
from flask import Blueprint

ipay_mock_mod = Blueprint('ipay_mock', __name__)

from . import views

