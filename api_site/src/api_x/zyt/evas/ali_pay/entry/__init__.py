# coding=utf-8
from __future__ import unicode_literals

from flask import Blueprint

ali_pay_entry_mod = Blueprint('ali_pay_entry', __name__, template_folder='./templates')

from . import pay_views, refund_views
