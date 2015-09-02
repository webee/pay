# -*- coding: utf-8 -*-
from flask import Blueprint


class PayType:
    BY_BALANCE = 0
    BY_BANKCARD = 1


pay_to_lvye_mod = Blueprint('pay_to_lvye', __name__, static_folder='static')

from . import pay_views


