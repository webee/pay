# coding=utf-8
from __future__ import unicode_literals

from flask import Blueprint

weixin_pay_entry_mod = Blueprint('weixin_pay_entry', __name__, template_folder='./templates')

from . import pay_views, refund_views
