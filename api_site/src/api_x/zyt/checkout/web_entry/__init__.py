# coding=utf-8
from __future__ import unicode_literals

from flask import Blueprint, render_template

web_checkout_entry_mod = Blueprint('web_checkout_entry', __name__)

from . import views
