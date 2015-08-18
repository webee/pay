# coding=utf-8
from __future__ import unicode_literals

from flask import Blueprint

test_pay_entry_mod = Blueprint('test_pay_entry', __name__, template_folder='./templates')

from . import pay_views, refund_views, pay_to_bankcard_views
