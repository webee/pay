# coding=utf-8
from __future__ import unicode_literals

from flask import Blueprint

main_entry_mod = Blueprint('main_entry', __name__)


from . import views, test_views, deprecated_views
