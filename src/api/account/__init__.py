# -*- coding: utf-8 -*-
from flask import Blueprint

account_mod = Blueprint('account', __name__)

from . import withdraw_views, account_views, bankcard_views, trading_views
