# coding=utf-8
from __future__ import unicode_literals

from flask import Blueprint

app_checkout_entry_mod = Blueprint('app_checkout_entry', __name__)

from . import views
