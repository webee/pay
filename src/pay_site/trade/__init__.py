# -*- coding: utf-8 -*-
from flask import Blueprint

trade_mod = Blueprint('trade', __name__, template_folder='', static_folder='static')

from . import pay_views
from . import cash_transfer_views
from pay_site.trade import refund_views, pay_views, cash_transfer_views
